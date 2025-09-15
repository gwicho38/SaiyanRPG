#!/usr/bin/env python3
"""
Issue Tracker for SaiyanQuest GTA Development
Helps track progress through the systematic implementation of features
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

class IssueStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class Issue:
    id: int
    title: str
    description: str
    tasks: List[str]
    acceptance_criteria: List[str]
    priority: Priority
    estimated_time: str
    status: IssueStatus = IssueStatus.PENDING
    assigned_to: str = ""
    created_date: str = ""
    started_date: str = ""
    completed_date: str = ""
    notes: str = ""
    dependencies: List[int] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if not self.created_date:
            self.created_date = datetime.now().isoformat()

class IssueTracker:
    """Tracks development issues and progress"""
    
    def __init__(self, data_file: str = "issue_tracker.json"):
        self.data_file = Path(data_file)
        self.issues: Dict[int, Issue] = {}
        self.current_issue: Optional[int] = None
        self.load_data()
    
    def load_data(self):
        """Load issues from file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for issue_data in data.get('issues', []):
                        # Convert string enums back to enum objects
                        issue_data['status'] = IssueStatus(issue_data['status'])
                        issue_data['priority'] = Priority(issue_data['priority'])
                        issue = Issue(**issue_data)
                        self.issues[issue.id] = issue
                    self.current_issue = data.get('current_issue')
            except Exception as e:
                print(f"Error loading data: {e}")
                # If there's an error, delete the corrupted file
                self.data_file.unlink(missing_ok=True)
    
    def save_data(self):
        """Save issues to file"""
        data = {
            'issues': [self._issue_to_dict(issue) for issue in self.issues.values()],
            'current_issue': self.current_issue
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _issue_to_dict(self, issue: Issue) -> dict:
        """Convert issue to dictionary with enum values"""
        issue_dict = asdict(issue)
        issue_dict['status'] = issue.status.value
        issue_dict['priority'] = issue.priority.value
        return issue_dict
    
    def add_issue(self, issue: Issue):
        """Add a new issue"""
        self.issues[issue.id] = issue
        self.save_data()
        print(f"✅ Added Issue #{issue.id}: {issue.title}")
    
    def start_issue(self, issue_id: int, assigned_to: str = ""):
        """Start working on an issue"""
        if issue_id not in self.issues:
            print(f"❌ Issue #{issue_id} not found")
            return
        
        issue = self.issues[issue_id]
        
        # Check dependencies
        for dep_id in issue.dependencies:
            if dep_id in self.issues and self.issues[dep_id].status != IssueStatus.COMPLETED:
                print(f"❌ Cannot start Issue #{issue_id}: Dependency Issue #{dep_id} not completed")
                return
        
        # Check if another issue is in progress
        for other_issue in self.issues.values():
            if other_issue.status == IssueStatus.IN_PROGRESS and other_issue.id != issue_id:
                print(f"❌ Cannot start Issue #{issue_id}: Issue #{other_issue.id} is already in progress")
                return
        
        issue.status = IssueStatus.IN_PROGRESS
        issue.assigned_to = assigned_to
        issue.started_date = datetime.now().isoformat()
        self.current_issue = issue_id
        self.save_data()
        
        print(f"🚀 Started Issue #{issue_id}: {issue.title}")
        print(f"   Assigned to: {assigned_to}")
        print(f"   Priority: {issue.priority.value}")
        print(f"   Estimated time: {issue.estimated_time}")
    
    def complete_issue(self, issue_id: int, notes: str = ""):
        """Mark an issue as completed"""
        if issue_id not in self.issues:
            print(f"❌ Issue #{issue_id} not found")
            return
        
        issue = self.issues[issue_id]
        issue.status = IssueStatus.COMPLETED
        issue.completed_date = datetime.now().isoformat()
        issue.notes = notes
        
        if self.current_issue == issue_id:
            self.current_issue = None
        
        self.save_data()
        
        print(f"🎉 Completed Issue #{issue_id}: {issue.title}")
        if notes:
            print(f"   Notes: {notes}")
    
    def block_issue(self, issue_id: int, reason: str = ""):
        """Block an issue"""
        if issue_id not in self.issues:
            print(f"❌ Issue #{issue_id} not found")
            return
        
        issue = self.issues[issue_id]
        issue.status = IssueStatus.BLOCKED
        issue.notes = reason
        self.save_data()
        
        print(f"🚫 Blocked Issue #{issue_id}: {issue.title}")
        if reason:
            print(f"   Reason: {reason}")
    
    def list_issues(self, status_filter: IssueStatus = None, priority_filter: Priority = None):
        """List issues with optional filtering"""
        filtered_issues = []
        
        for issue in self.issues.values():
            if status_filter and issue.status != status_filter:
                continue
            if priority_filter and issue.priority != priority_filter:
                continue
            filtered_issues.append(issue)
        
        # Sort by priority (high first) then by ID
        filtered_issues.sort(key=lambda x: (x.priority.value == 'low', x.priority.value == 'medium', x.id))
        
        if not filtered_issues:
            print("No issues found matching criteria")
            return
        
        print(f"\n📋 Issues ({len(filtered_issues)} found):")
        print("=" * 80)
        
        for issue in filtered_issues:
            status_emoji = {
                IssueStatus.PENDING: "⏳",
                IssueStatus.IN_PROGRESS: "🚀",
                IssueStatus.COMPLETED: "✅",
                IssueStatus.BLOCKED: "🚫",
                IssueStatus.CANCELLED: "❌"
            }
            
            priority_emoji = {
                Priority.HIGH: "🔴",
                Priority.MEDIUM: "🟡",
                Priority.LOW: "🟢"
            }
            
            print(f"{status_emoji[issue.status]} #{issue.id}: {issue.title}")
            print(f"   {priority_emoji[issue.priority]} Priority: {issue.priority.value.upper()}")
            print(f"   ⏱️  Estimated: {issue.estimated_time}")
            if issue.assigned_to:
                print(f"   👤 Assigned: {issue.assigned_to}")
            if issue.status == IssueStatus.IN_PROGRESS:
                print(f"   📅 Started: {issue.started_date[:10]}")
            elif issue.status == IssueStatus.COMPLETED:
                print(f"   📅 Completed: {issue.completed_date[:10]}")
            print()
    
    def show_current_issue(self):
        """Show details of current issue"""
        if not self.current_issue:
            print("No issue currently in progress")
            return
        
        issue = self.issues[self.current_issue]
        print(f"\n🚀 Current Issue: #{issue.id}")
        print("=" * 50)
        print(f"Title: {issue.title}")
        print(f"Priority: {issue.priority.value.upper()}")
        print(f"Estimated Time: {issue.estimated_time}")
        print(f"Assigned to: {issue.assigned_to}")
        print(f"Started: {issue.started_date[:10]}")
        
        print(f"\n📝 Description:")
        print(issue.description)
        
        print(f"\n✅ Tasks:")
        for i, task in enumerate(issue.tasks, 1):
            print(f"   {i}. {task}")
        
        print(f"\n🎯 Acceptance Criteria:")
        for i, criteria in enumerate(issue.acceptance_criteria, 1):
            print(f"   {i}. {criteria}")
        
        if issue.dependencies:
            print(f"\n🔗 Dependencies:")
            for dep_id in issue.dependencies:
                dep_issue = self.issues.get(dep_id)
                if dep_issue:
                    status_emoji = "✅" if dep_issue.status == IssueStatus.COMPLETED else "⏳"
                    print(f"   {status_emoji} #{dep_id}: {dep_issue.title}")
    
    def get_next_issue(self) -> Optional[Issue]:
        """Get the next issue to work on"""
        # Find highest priority pending issue with no incomplete dependencies
        pending_issues = [issue for issue in self.issues.values() 
                         if issue.status == IssueStatus.PENDING]
        
        for priority in [Priority.HIGH, Priority.MEDIUM, Priority.LOW]:
            for issue in pending_issues:
                if issue.priority == priority:
                    # Check dependencies
                    deps_complete = True
                    for dep_id in issue.dependencies:
                        if dep_id not in self.issues or self.issues[dep_id].status != IssueStatus.COMPLETED:
                            deps_complete = False
                            break
                    
                    if deps_complete:
                        return issue
        
        return None
    
    def show_progress(self):
        """Show overall progress"""
        total_issues = len(self.issues)
        completed = sum(1 for issue in self.issues.values() if issue.status == IssueStatus.COMPLETED)
        in_progress = sum(1 for issue in self.issues.values() if issue.status == IssueStatus.IN_PROGRESS)
        pending = sum(1 for issue in self.issues.values() if issue.status == IssueStatus.PENDING)
        blocked = sum(1 for issue in self.issues.values() if issue.status == IssueStatus.BLOCKED)
        
        print(f"\n📊 Progress Overview:")
        print("=" * 30)
        print(f"Total Issues: {total_issues}")
        print(f"✅ Completed: {completed} ({completed/total_issues*100:.1f}%)")
        print(f"🚀 In Progress: {in_progress}")
        print(f"⏳ Pending: {pending}")
        print(f"🚫 Blocked: {blocked}")
        
        if completed > 0:
            print(f"\n🎉 Completion Rate: {completed/total_issues*100:.1f}%")

def create_default_issues(tracker: IssueTracker):
    """Create the default issues from the roadmap"""
    
    issues_data = [
        {
            "id": 1,
            "title": "Upgrade Physics System to Box2D Integration",
            "description": "Upgrade the current basic pygame physics to a comprehensive Box2D-based physics system for realistic vehicle and character physics.",
            "tasks": [
                "Install and integrate PyBox2D",
                "Create PhysicsManager class", 
                "Implement vehicle physics bodies",
                "Add collision detection",
                "Integrate with existing vehicle system",
                "Add physics debugging tools"
            ],
            "acceptance_criteria": [
                "Vehicles have realistic physics simulation",
                "Collision detection works properly", 
                "Performance is acceptable (60fps with 10+ vehicles)",
                "Integration with existing code is seamless"
            ],
            "priority": Priority.HIGH,
            "estimated_time": "1-2 weeks",
            "dependencies": []
        },
        {
            "id": 2,
            "title": "Implement Advanced Vehicle Features (Damage, Passengers, Animations)",
            "description": "Implement comprehensive vehicle features inspired by Carnage3D including damage system, passenger management, door animations, and emergency lights.",
            "tasks": [
                "Implement damage system",
                "Add passenger management",
                "Create door animations", 
                "Add emergency lights",
                "Implement tire physics",
                "Add vehicle effects (fire, smoke)",
                "Create repair mechanics"
            ],
            "acceptance_criteria": [
                "Vehicles can take damage and show visual effects",
                "Passengers can enter/exit vehicles properly",
                "Emergency lights work",
                "Vehicle handling feels realistic", 
                "All vehicle states (normal, damaged, burning) work"
            ],
            "priority": Priority.HIGH,
            "estimated_time": "2-3 weeks",
            "dependencies": [1]  # Depends on physics system
        },
        {
            "id": 3,
            "title": "Enhance Character AI with Fear Responses and Advanced Behaviors",
            "description": "Implement advanced AI behaviors for pedestrians including fear responses, vehicle interactions, and complex animation states.",
            "tasks": [
                "Implement character states (idle, walking, shooting, etc.)",
                "Add fear/response system",
                "Create advanced AI behaviors",
                "Implement weapon inventory",
                "Add health and armor systems", 
                "Create animation state machine",
                "Add vehicle interaction"
            ],
            "acceptance_criteria": [
                "Characters have realistic AI behaviors",
                "Characters respond to environment (gunshots, police)",
                "Animation system works smoothly",
                "Character-vehicle interaction is seamless",
                "Health and damage systems work properly"
            ],
            "priority": Priority.HIGH,
            "estimated_time": "2-3 weeks",
            "dependencies": [1]  # Depends on physics system
        },
        {
            "id": 4,
            "title": "Implement 3D World System with Multiple Layers",
            "description": "Add 3D world system with multiple layers and improved collision detection, building on the existing pixel art map system.",
            "tasks": [
                "Create 3D tile array system",
                "Implement district management",
                "Add water level support",
                "Create collision tracing",
                "Implement map data loading",
                "Add pathfinding support",
                "Integrate with existing TMX system"
            ],
            "acceptance_criteria": [
                "World supports multiple layers",
                "Districts work properly",
                "Collision detection is accurate",
                "Map loading is efficient",
                "Integration with TMX maps is seamless"
            ],
            "priority": Priority.HIGH,
            "estimated_time": "3-4 weeks",
            "dependencies": []
        },
        {
            "id": 5,
            "title": "Implement Traffic Management with AI-Controlled Vehicles",
            "description": "Create a comprehensive traffic management system with AI-controlled vehicles and dynamic spawning.",
            "tasks": [
                "Implement vehicle spawning and despawning",
                "Add traffic flow management",
                "Create AI vehicle behavior",
                "Add traffic density control",
                "Implement traffic rules and patterns"
            ],
            "acceptance_criteria": [
                "Traffic vehicles spawn and despawn dynamically",
                "AI vehicles follow realistic driving patterns",
                "Traffic density is configurable",
                "Performance remains stable with many vehicles"
            ],
            "priority": Priority.MEDIUM,
            "estimated_time": "2-3 weeks",
            "dependencies": [1, 2]  # Depends on physics and vehicle systems
        }
    ]
    
    for issue_data in issues_data:
        issue = Issue(**issue_data)
        tracker.add_issue(issue)

def main():
    """Main CLI interface"""
    tracker = IssueTracker()
    
    # Create default issues if none exist
    if not tracker.issues:
        print("🎯 Creating default issues from roadmap...")
        create_default_issues(tracker)
    
    print("\n🎮 SaiyanQuest GTA - Issue Tracker")
    print("=" * 50)
    
    while True:
        print("\nCommands:")
        print("  list [status] [priority] - List issues")
        print("  start <id> [assignee]    - Start working on issue")
        print("  complete <id> [notes]    - Mark issue as completed")
        print("  block <id> [reason]      - Block issue")
        print("  current                  - Show current issue details")
        print("  next                     - Show next issue to work on")
        print("  progress                 - Show overall progress")
        print("  quit                     - Exit")
        
        try:
            command = input("\n> ").strip().split()
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd == "list":
                status_filter = None
                priority_filter = None
                
                if len(command) > 1:
                    status_map = {"pending": IssueStatus.PENDING, "in_progress": IssueStatus.IN_PROGRESS,
                                 "completed": IssueStatus.COMPLETED, "blocked": IssueStatus.BLOCKED}
                    if command[1] in status_map:
                        status_filter = status_map[command[1]]
                
                if len(command) > 2:
                    priority_map = {"high": Priority.HIGH, "medium": Priority.MEDIUM, "low": Priority.LOW}
                    if command[2] in priority_map:
                        priority_filter = priority_map[command[2]]
                
                tracker.list_issues(status_filter, priority_filter)
            
            elif cmd == "start":
                if len(command) < 2:
                    print("Usage: start <id> [assignee]")
                    continue
                issue_id = int(command[1])
                assignee = command[2] if len(command) > 2 else ""
                tracker.start_issue(issue_id, assignee)
            
            elif cmd == "complete":
                if len(command) < 2:
                    print("Usage: complete <id> [notes]")
                    continue
                issue_id = int(command[1])
                notes = " ".join(command[2:]) if len(command) > 2 else ""
                tracker.complete_issue(issue_id, notes)
            
            elif cmd == "block":
                if len(command) < 2:
                    print("Usage: block <id> [reason]")
                    continue
                issue_id = int(command[1])
                reason = " ".join(command[2:]) if len(command) > 2 else ""
                tracker.block_issue(issue_id, reason)
            
            elif cmd == "current":
                tracker.show_current_issue()
            
            elif cmd == "next":
                next_issue = tracker.get_next_issue()
                if next_issue:
                    print(f"\n🎯 Next Issue: #{next_issue.id}")
                    print(f"Title: {next_issue.title}")
                    print(f"Priority: {next_issue.priority.value.upper()}")
                    print(f"Estimated Time: {next_issue.estimated_time}")
                else:
                    print("No pending issues available")
            
            elif cmd == "progress":
                tracker.show_progress()
            
            elif cmd == "quit":
                break
            
            else:
                print("Unknown command")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()