#! /usr/bin/env python3

import argparse
from datetime import datetime
import timew
from fpdf import FPDF

# PDF Report Generation Function
def generate_timesheet(data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, 'Monthly Timesheet Report', ln=True, align='C')
    pdf.ln(10)

    # Summary Table
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 8, 'Date', 1)
    pdf.cell(120, 8, 'Comment', 1)
    pdf.cell(30, 8, 'Time (HH:MM)', 1)
    pdf.ln()

    pdf.set_font('Arial', '', 10)
    total_duration = 0
    for entry in data:
        # Calculate the height needed for the tags cell
        tags_height = pdf.get_string_width(entry['tags']) // 100 * 8 + 8
        cell_height = max(8.0, tags_height)
        pdf.cell(40, cell_height, entry['date'], 1)
        pdf.multi_cell(120, 8, entry['tags'], 1)
        x, y = pdf.get_x(), pdf.get_y()
        pdf.set_xy(x + 160, y - 8)  # Move cursor to the correct position after multi_cell
        total_hours = entry['total_time'].seconds // 3600
        total_minutes = (entry['total_time'].seconds % 3600) // 60
        formatted_time = f"{total_hours:02}:{total_minutes:02}"
        pdf.cell(30, cell_height, formatted_time, 1, align='R')
        total_duration += entry['total_time'].total_seconds()
        pdf.ln()

    # Add a summary line for total time below the Total Time column
    pdf.set_font('Arial', 'B', 10)
    total_hours = int(total_duration // 3600)
    total_minutes = int((total_duration % 3600) // 60)
    formatted_total_time = f"{total_hours:3}:{total_minutes:02}"
    pdf.cell(160, 8, 'Total Time', 1, align='R')
    pdf.cell(30, 8, formatted_total_time, 1, align='R')
    pdf.ln()

    filename = f"timesheet_{datetime.now().strftime('%Y%m%d')}.pdf"
    pdf.output(filename)
    print(f"Timesheet generated: {filename}")

# Example Timewarrior Data Extraction Script (Modify as needed)
def get_timew_data(project_name, start_date, end_date):
    # Start timewarrior client (edit the path to your installation)
    tw = timew.TimeWarrior('/usr/local/bin/timew')

    # Collect data from Timewarrior using filters
    reports = tw.summary(f'{start_date}', f'{end_date}')

    data = []
    for report in reports:
        # Skip entries that do not have the project_name tag
        if report['tags'][0] != project_name:
            continue

        # Convert start and end times to datetime objects and calculate total time
        start_time = datetime.strptime(report['start'], '%Y%m%dT%H%M%SZ')
        end_time = datetime.strptime(report['end'], '%Y%m%dT%H%M%SZ')
        total_time = end_time - start_time
        tags = report['tags'][1:]

        entry = {
            'date': start_time.strftime('%Y-%m-%d'),
            'tags': ', '.join(tags),
            'total_time': total_time
        }
        data.append(entry)

    # Sort data by start date
    data.sort(key=lambda x: x['date'])

    return data

# Main function to generate timesheet for a given project and time range
def main():
    parser = argparse.ArgumentParser(description="Generate a timesheet PDF from Timewarrior data.")
    parser.add_argument("--project", type=str, required=True, help="The project name to filter the data.")
    parser.add_argument("--start", type=str, required=True, help="The start date for the timesheet (YYYY-MM-DD).")
    parser.add_argument("--end", type=str, required=True, help="The end date for the timesheet (YYYY-MM-DD).")
    args = parser.parse_args()

    project_name = args.project
    start_date = args.start
    end_date = args.end

    data = get_timew_data(project_name, start_date, end_date)
    generate_timesheet(data)

if __name__ == "__main__":
    main()
