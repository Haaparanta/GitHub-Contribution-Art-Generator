import os
import subprocess
from datetime import datetime, timedelta
import numpy as np
from pixel_art import pixel_art

def is_leap_year(year):
    """Check if a year is a leap year."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def display_grid(grid, show_days=False, start_date=None):
    """Display the grid with optional day markers."""
    if show_days and start_date:
        dates = [(start_date + timedelta(days=i)).strftime('%a')[0].lower() for i in range(7 * len(grid[0]))]
        for i, row in enumerate(grid):
            day_string = ' '.join([dates[i + 7 * week] for week in range(len(grid[0]))])
            print(day_string)
    else:
        for row in grid:
            print(' '.join(['#' if cell == 5 else '.' for cell in row]))

def create_commits(grid, start_date):
    """Create commits based on the grid pattern."""
    for week in range(len(grid[0])):
        for day in range(7):
            commit_count = grid[day][week]
            if day == 6:  # Saturday to the same day next week
                commit_date = start_date + timedelta(weeks=week + 1, days=0)
            elif day == 0:  # Sunday to Monday
                commit_date = start_date + timedelta(weeks=week, days=1)
            else:
                commit_date = start_date + timedelta(weeks=week, days=day + 1)
            formatted_date = commit_date.strftime('%Y-%m-%dT%H:%M:%S')
            os.environ['GIT_COMMITTER_DATE'] = formatted_date
            os.environ['GIT_AUTHOR_DATE'] = formatted_date
            for _ in range(commit_count):
                subprocess.call(['git', 'commit', '--allow-empty', '-m', 'Commit for graph', '--date', formatted_date])

def text_to_grid(text, width, height):
    """Convert text to a grid representation with specified width and height."""
    char_height = 7
    char_width = 5
    spacing = 1

    grid = np.zeros((height, width), dtype=int)

    x_offset = 0
    y_offset = 0  # Align the text to the top

    for char in text:
        if char in pixel_art:
            char_pixels = pixel_art[char]
            for y in range(char_height):
                for x in range(char_width):
                    if char_pixels[y][x] == '#':
                        grid[y_offset + y, x_offset + x] = 5
            x_offset += char_width + spacing
            if x_offset + char_width > width:
                break  # Stop if we run out of width
        else:
            print(f"Character '{char}' not defined in pixel art.")
    
    # Ensure at least one commit per day
    for week in range(width):
        for day in range(height):
            if grid[day][week] == 0:
                grid[day][week] = 1

    return grid

def calculate_start_date(year):
    """Calculate the start date for the contribution graph, ensuring it starts on a Sunday."""
    start_date = datetime(year, 1, 2)
    while start_date.weekday() != 6:  # Ensure start on Sunday
        start_date += timedelta(days=1)
    return start_date

def switch_to_year_branch(year):
    """Switch to a branch named after the year, creating it if it doesn't exist."""
    branch_name = str(year)
    subprocess.call(['git', 'checkout', '-b', branch_name])
    subprocess.call(['git', 'checkout', branch_name])

def main():
    year = int(input("Enter the year for the contribution graph: "))
    text = input("Enter the text to display: ")

    width = 52
    height = 7
    start_date = calculate_start_date(year)

    grid = text_to_grid(text, width=width, height=height)

    print("\nPreview of the contribution graph:")
    display_grid(grid)

    confirm = input("\nDo you want to proceed with creating the commits? (yes/no): ").strip().lower()
    if confirm == 'yes':
        switch_to_year_branch(year)
        create_commits(grid, start_date)
        print("Commits created successfully.")
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main()