import requests
import psutil
import time
import sys

def get_session_id():
    """
    Get your session ID from browser cookies.
    You'll need to manually copy this from your browser.
    """
    # TODO: Replace with your actual session_id
    return "KqVyYADYmkkfht9Y4xPDivkXRXWypqDuIlJbNFK87QI"

def check_goal():
    """Check if weekly running goal is met"""
    session_id = get_session_id()
    
    try:
        response = requests.get(
            'http://localhost:8000/check-goal',
            cookies={'session_id': session_id}
        )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return None
        
        return response.json()
        
    except Exception as e:
        print(f"Failed to check goal: {e}")
        return None

def kill_steam():
    """Kill Steam process if running"""
    killed = False
    for proc in psutil.process_iter(['name']):
        try:
            if 'steam' in proc.info['name'].lower():
                proc.kill()
                print(f"Killed process: {proc.info['name']}")
                killed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    return killed

def check_and_enforce():
    """Main enforcement logic"""
    data = check_goal()
    
    if not data:
        print("Could not fetch goal status")
        return
    
    print(f"\n{'='*50}")
    print(f"Goal: {data['goal_miles']} miles")
    print(f"Actual: {data['actual_miles']} miles")
    print(f"Progress: {data['percentage']:.1f}%")
    print(f"Goal met: {data['goal_met']}")
    print(f"{'='*50}\n")
    
    if not data['goal_met']:
        print(f"❌ Goal not met! Need {data['remaining_miles']} more miles.")
        print("Blocking Steam...")
        if kill_steam():
            print("Steam has been blocked.")
        else:
            print("Steam was not running.")
    else:
        print(f"✅ Goal met! Steam allowed.")

if __name__ == "__main__":
    print("Steam Blocker - Running goal check...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            check_and_enforce()
            time.sleep(3600)  # Check every hour
    except KeyboardInterrupt:
        print("\nStopping Steam Blocker...")
        sys.exit(0)