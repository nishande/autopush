import os
import git
from datetime import datetime, timedelta
import json
from pathlib import Path
import pytz  # We'll use this for timezone handling

class GitBackdater:
    def __init__(self):
        self.config_file = "commit_config.json"
        self.last_commit_date = None
        self.repo = None
        self.load_config()
        
        # Set up git configuration
        self.setup_git_config()

    def setup_git_config(self):
        """Setup basic git configuration if not exists"""
        try:
            if not self.repo:
                self.init_repo()
            with self.repo.config_writer() as git_config:
                if not git_config.has_section('user'):
                    git_config.add_section('user')
                git_config.set_value('user', 'email', 'your.email@example.com')
                git_config.set_value('user', 'name', 'Your Name')
        except Exception as e:
            print(f"Error setting up git config: {str(e)}")

    def load_config(self):
        """Load the last commit date from config file if it exists"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                date_str = config.get('last_commit_date')
                if date_str:
                    self.last_commit_date = datetime.strptime(date_str, '%Y-%m-%d')

    def save_config(self):
        """Save the last commit date to config file"""
        with open(self.config_file, 'w') as f:
            json.dump({
                'last_commit_date': self.last_commit_date.strftime('%Y-%m-%d')
            }, f)

    def init_repo(self):
        """Initialize git repository if it doesn't exist"""
        try:
            self.repo = git.Repo('.')
            print("Repository already exists!")
        except git.exc.InvalidGitRepositoryError:
            self.repo = git.Repo.init('.')
            print("Initialized new Git repository")

    def get_commit_date(self):
        """Get the commit date either from user input or next day from last commit"""
        if not self.last_commit_date:
            while True:
                date_str = input("Enter the starting date (YYYY-MM-DD): ")
                try:
                    self.last_commit_date = datetime.strptime(date_str, '%Y-%m-%d')
                    break
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD")
        else:
            self.last_commit_date += timedelta(days=1)
        
        # Add timezone information
        timezone = pytz.timezone('UTC')
        return timezone.localize(self.last_commit_date)

    def commit_file(self, file_path, commit_message=None):
        """Commit a file with backdated timestamp"""
        try:
            # Add file to git
            self.repo.index.add([file_path])
            
            # Get commit date
            commit_date = self.get_commit_date()
            
            # Create commit message if not provided
            if not commit_message:
                commit_message = f"Updated {file_path}"

            # Create the commit with the backdated timestamp
            self.repo.index.commit(
                commit_message,
                author_date=commit_date,
                commit_date=commit_date,
                author=git.Actor("Your Name", "your.email@example.com")
            )
            
            # Save the commit date to config
            self.save_config()
            
            print(f"Successfully committed {file_path} with date: {commit_date.strftime('%Y-%m-%d')}")
            
        except Exception as e:
            print(f"Error committing file: {str(e)}")

def main():
    git_backdater = GitBackdater()
    git_backdater.init_repo()

    while True:
        print("\n1. Create and commit new file")
        print("2. Commit existing file")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")

        if choice == '1':
            file_name = input("Enter new file name: ")
            content = input("Enter file content: ")
            
            # Create new file
            with open(file_name, 'w') as f:
                f.write(content)
            
            git_backdater.commit_file(file_name)

        elif choice == '2':
            file_name = input("Enter existing file name: ")
            if os.path.exists(file_name):
                git_backdater.commit_file(file_name)
            else:
                print("File does not exist!")

        elif choice == '3':
            print("Exiting...")
            break

        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()