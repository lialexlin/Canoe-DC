"""
Progress Tracker for Bulk Document Processing
Tracks processing state and allows resuming from interruptions
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from loguru import logger


class ProgressTracker:
    """Track and persist processing progress for bulk operations"""
    
    def __init__(self, session_name: Optional[str] = None):
        """Initialize progress tracker with optional session name"""
        self.progress_dir = Path("data/progress")
        self.progress_dir.mkdir(parents=True, exist_ok=True)
        
        # Create session file
        if session_name:
            self.session_file = self.progress_dir / f"{session_name}.json"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.session_file = self.progress_dir / f"session_{timestamp}.json"
        
        # Initialize progress data
        self.progress_data = {
            "session_start": datetime.now().isoformat(),
            "session_file": str(self.session_file),
            "total_documents": 0,
            "processed_count": 0,
            "failed_count": 0,
            "documents": [],
            "processed_documents": [],
            "failed_documents": [],
            "remaining_documents": [],
            "processing_times": [],
            "last_checkpoint": None,
            "status": "initialized"
        }
        
        # Track failed documents separately for retry
        self.failed_docs_file = self.progress_dir / "failed_documents.json"
        
    def load_session(self, session_file: str) -> bool:
        """Load an existing session for resuming"""
        try:
            session_path = Path(session_file)
            if not session_path.exists():
                session_path = self.progress_dir / session_file
            
            if session_path.exists():
                with open(session_path, 'r') as f:
                    self.progress_data = json.load(f)
                self.session_file = session_path
                logger.info(f"📂 Loaded session from {session_path}")
                logger.info(f"   Processed: {self.progress_data['processed_count']}/{self.progress_data['total_documents']}")
                logger.info(f"   Failed: {self.progress_data['failed_count']}")
                return True
            else:
                logger.warning(f"Session file not found: {session_file}")
                return False
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return False
    
    def initialize_documents(self, documents: List[Dict[str, Any]]):
        """Initialize the list of documents to process"""
        self.progress_data["documents"] = documents
        self.progress_data["total_documents"] = len(documents)
        self.progress_data["remaining_documents"] = [doc['id'] for doc in documents]
        self.progress_data["status"] = "initialized"
        self.save_progress()
        
        # Display document list
        logger.info(f"\n📋 Documents to process ({len(documents)} total):")
        logger.info("="*60)
        for i, doc in enumerate(documents[:10], 1):  # Show first 10
            doc_name = doc.get('name', 'Unknown')
            doc_id = doc.get('id', 'N/A')
            doc_type = doc.get('document_type', 'N/A')
            logger.info(f"  {i:3d}. {doc_name[:40]:<40} (ID: {doc_id[:8]}... Type: {doc_type})")
        
        if len(documents) > 10:
            logger.info(f"  ... and {len(documents) - 10} more documents")
        logger.info("="*60 + "\n")
    
    def mark_processing(self, document_id: str, document_name: str):
        """Mark a document as currently being processed"""
        self.progress_data["status"] = "processing"
        self.progress_data["current_document"] = {
            "id": document_id,
            "name": document_name,
            "start_time": datetime.now().isoformat()
        }
        self.save_progress()
    
    def mark_completed(self, document_id: str, document_name: str, summary: Optional[str] = None):
        """Mark a document as successfully processed"""
        # Calculate processing time
        if "current_document" in self.progress_data:
            start_time = datetime.fromisoformat(self.progress_data["current_document"]["start_time"])
            processing_time = (datetime.now() - start_time).total_seconds()
            self.progress_data["processing_times"].append(processing_time)
        
        # Update counters
        self.progress_data["processed_count"] += 1
        self.progress_data["processed_documents"].append({
            "id": document_id,
            "name": document_name,
            "completed_at": datetime.now().isoformat(),
            "summary_length": len(summary) if summary else 0
        })
        
        # Remove from remaining
        if document_id in self.progress_data["remaining_documents"]:
            self.progress_data["remaining_documents"].remove(document_id)
        
        # Clear current document
        self.progress_data.pop("current_document", None)
        self.progress_data["last_checkpoint"] = datetime.now().isoformat()
        
        # Update status
        if self.progress_data["processed_count"] + self.progress_data["failed_count"] >= self.progress_data["total_documents"]:
            self.progress_data["status"] = "completed"
        
        self.save_progress()
        self.display_progress()
    
    def mark_failed(self, document_id: str, document_name: str, error: str):
        """Mark a document as failed"""
        self.progress_data["failed_count"] += 1
        failed_doc = {
            "id": document_id,
            "name": document_name,
            "error": str(error),
            "failed_at": datetime.now().isoformat()
        }
        self.progress_data["failed_documents"].append(failed_doc)
        
        # Remove from remaining
        if document_id in self.progress_data["remaining_documents"]:
            self.progress_data["remaining_documents"].remove(document_id)
        
        # Clear current document
        self.progress_data.pop("current_document", None)
        
        # Save to separate failed documents file
        self.save_failed_documents()
        
        # Update status
        if self.progress_data["processed_count"] + self.progress_data["failed_count"] >= self.progress_data["total_documents"]:
            self.progress_data["status"] = "completed"
        
        self.save_progress()
        self.display_progress()
    
    def save_progress(self):
        """Save current progress to file"""
        try:
            with open(self.session_file, 'w') as f:
                json.dump(self.progress_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
    
    def save_failed_documents(self):
        """Save failed documents to a separate file for retry"""
        try:
            failed_data = {
                "session": str(self.session_file),
                "timestamp": datetime.now().isoformat(),
                "failed_documents": self.progress_data["failed_documents"]
            }
            
            # Load existing failed documents if file exists
            if self.failed_docs_file.exists():
                with open(self.failed_docs_file, 'r') as f:
                    existing_data = json.load(f)
                    # Merge with existing failed documents
                    existing_ids = {doc['id'] for doc in existing_data.get('failed_documents', [])}
                    for doc in failed_data['failed_documents']:
                        if doc['id'] not in existing_ids:
                            existing_data['failed_documents'].append(doc)
                    failed_data = existing_data
            
            with open(self.failed_docs_file, 'w') as f:
                json.dump(failed_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save failed documents: {e}")
    
    def display_progress(self):
        """Display current progress bar and statistics"""
        total = self.progress_data["total_documents"]
        processed = self.progress_data["processed_count"]
        failed = self.progress_data["failed_count"]
        
        if total == 0:
            return
        
        # Calculate percentage
        completed = processed + failed
        percentage = (completed / total) * 100
        
        # Create progress bar
        bar_length = 40
        filled_length = int(bar_length * completed / total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Calculate average processing time
        avg_time = 0
        if self.progress_data["processing_times"]:
            avg_time = sum(self.progress_data["processing_times"]) / len(self.progress_data["processing_times"])
        
        # Display progress
        logger.info(f"\n📊 Progress: [{bar}] {completed}/{total} ({percentage:.1f}%)")
        logger.info(f"   ✅ Processed: {processed} | ❌ Failed: {failed} | ⏱️ Avg time: {avg_time:.1f}s")
        
        # Estimate remaining time
        if avg_time > 0 and (total - completed) > 0:
            remaining_time = avg_time * (total - completed)
            logger.info(f"   ⏳ Estimated time remaining: {remaining_time/60:.1f} minutes")
    
    def get_remaining_documents(self) -> List[str]:
        """Get list of document IDs that haven't been processed"""
        return self.progress_data.get("remaining_documents", [])
    
    def get_failed_documents(self) -> List[Dict[str, Any]]:
        """Get list of failed documents for retry"""
        return self.progress_data.get("failed_documents", [])
    
    def generate_summary_report(self) -> str:
        """Generate a final summary report"""
        report = []
        report.append("\n" + "="*60)
        report.append("📊 PROCESSING SUMMARY REPORT")
        report.append("="*60)
        
        total = self.progress_data["total_documents"]
        processed = self.progress_data["processed_count"]
        failed = self.progress_data["failed_count"]
        
        report.append(f"\n📈 Overall Statistics:")
        report.append(f"   Total Documents: {total}")
        report.append(f"   Successfully Processed: {processed} ({(processed/total*100):.1f}%)")
        report.append(f"   Failed: {failed} ({(failed/total*100):.1f}%)")
        
        # Processing time statistics
        if self.progress_data["processing_times"]:
            times = self.progress_data["processing_times"]
            report.append(f"\n⏱️ Processing Times:")
            report.append(f"   Total Time: {sum(times)/60:.1f} minutes")
            report.append(f"   Average per Document: {sum(times)/len(times):.1f} seconds")
            report.append(f"   Fastest: {min(times):.1f} seconds")
            report.append(f"   Slowest: {max(times):.1f} seconds")
        
        # Failed documents
        if self.progress_data["failed_documents"]:
            report.append(f"\n❌ Failed Documents ({len(self.progress_data['failed_documents'])}):")
            for doc in self.progress_data["failed_documents"][:5]:
                report.append(f"   - {doc['name'][:40]}: {doc['error'][:50]}")
            if len(self.progress_data["failed_documents"]) > 5:
                report.append(f"   ... and {len(self.progress_data['failed_documents']) - 5} more")
            report.append(f"\n   💡 To retry failed documents, run with --retry-failed flag")
        
        # Session info
        report.append(f"\n📁 Session Information:")
        report.append(f"   Session File: {self.session_file}")
        report.append(f"   Started: {self.progress_data['session_start']}")
        if self.progress_data.get('last_checkpoint'):
            report.append(f"   Last Checkpoint: {self.progress_data['last_checkpoint']}")
        
        report.append("\n" + "="*60)
        
        return "\n".join(report)
    
    def should_resume(self) -> bool:
        """Check if there are remaining documents to process"""
        return len(self.progress_data.get("remaining_documents", [])) > 0
    
    @staticmethod
    def get_latest_session() -> Optional[str]:
        """Get the most recent session file"""
        progress_dir = Path("data/progress")
        if not progress_dir.exists():
            return None
        
        session_files = list(progress_dir.glob("session_*.json"))
        if not session_files:
            return None
        
        # Sort by modification time and return the latest
        latest = max(session_files, key=lambda p: p.stat().st_mtime)
        return str(latest)
    
    @staticmethod
    def load_failed_documents() -> List[Dict[str, Any]]:
        """Load all failed documents from the failed documents file"""
        failed_docs_file = Path("data/progress/failed_documents.json")
        if not failed_docs_file.exists():
            return []
        
        try:
            with open(failed_docs_file, 'r') as f:
                data = json.load(f)
                return data.get("failed_documents", [])
        except Exception as e:
            logger.error(f"Failed to load failed documents: {e}")
            return []