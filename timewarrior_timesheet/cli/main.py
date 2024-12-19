from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional

import timew
import typer
from fpdf import FPDF, XPos, YPos

from timewarrior_timesheet import __version__

app = typer.Typer(
    no_args_is_help=True,
    add_completion=True,
    invoke_without_command=True,
)


# PDF Report Generation Function
def generate_timesheet(data,
                       output_path: Optional[Path] = Path.cwd()):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(
        200,
        10,
        f"{datetime.strptime(data[0]['date'], '%Y-%m-%d').strftime('%B %Y')} Timesheet",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
        align="C",
    )
    pdf.ln(10)

    # Summary Table
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(40, 8, "Date", 1)
    pdf.cell(120, 8, "Comment", 1)
    pdf.cell(30, 8, "Time (HH:MM)", 1)
    pdf.ln()

    pdf.set_font("Helvetica", "", 10)
    total_duration = 0
    for entry in data:
        # Calculate the height needed for the row based on the length of the comment
        tags_width = 120
        line_height = 8
        num_lines = max(1, int(pdf.get_string_width(entry["tags"]) / tags_width) + 1)
        cell_height = line_height * num_lines

        # Set all cells in the row to the calculated height
        pdf.cell(40, cell_height, entry["date"], 1)
        pdf.multi_cell(tags_width, line_height, entry["tags"], 1)
        x_after = pdf.get_x()
        y_after = pdf.get_y()
        pdf.set_xy(x_after, y_after - cell_height)

        total_hours = entry["total_time"].seconds // 3600
        total_minutes = (entry["total_time"].seconds % 3600) // 60
        formatted_time = f"{total_hours:02}:{total_minutes:02}"
        pdf.cell(30, cell_height, formatted_time, 1, align="R")
        total_duration += entry["total_time"].total_seconds()
        pdf.ln(cell_height)

    # Add a summary line for total time below the Total Time column
    pdf.set_font("Helvetica", "B", 10)
    total_hours = int(total_duration // 3600)
    total_minutes = int((total_duration % 3600) // 60)
    formatted_total_time = f"{total_hours:02}:{total_minutes:02}"
    pdf.cell(160, 8, "Total Time", 1, align="R")
    pdf.cell(30, 8, formatted_total_time, 1, align="R")
    pdf.ln()

    filename = output_path / f"timesheet_{datetime.strptime(data[0]['date'], '%Y-%m-%d').strftime('%m_%Y')}.pdf"
    pdf.output(filename)
    print(f"Timesheet generated: {filename}")


# Example Timewarrior Data Extraction Script (Modify as needed)
def get_timew_data(project_name, start_date, end_date):
    # Start timewarrior client (edit the path to your installation)
    tw = timew.TimeWarrior("/usr/local/bin/timew")

    # Collect data from Timewarrior using filters
    reports = tw.summary(f"{start_date}", f"{end_date}")

    aggregated_data = {}
    for report in reports:
        # Skip entries that do not have the project_name tag
        if report["tags"][0] != project_name:
            continue

        # Convert start and end times to datetime objects and calculate total time
        start_time = datetime.strptime(report["start"], "%Y%m%dT%H%M%SZ")
        end_time = datetime.strptime(report["end"], "%Y%m%dT%H%M%SZ")
        total_time = end_time - start_time
        tags = ", ".join(report["tags"][1:])

        # Key to aggregate by date and tags
        key = (start_time.strftime("%Y-%m-%d"), tags)
        if key in aggregated_data:
            aggregated_data[key] += total_time
        else:
            aggregated_data[key] = total_time

    data = []
    for (date, tags), total_time in aggregated_data.items():
        entry = {"date": date, "tags": tags, "total_time": total_time}
        data.append(entry)

    # Sort data by start date
    data.sort(key=lambda x: x["date"])

    return data


def version_callback(value: bool):
    if value:
        typer.echo(f"Timesheet Generator v{__version__}")
        raise typer.Exit()


# Main function to generate timesheet for a given project and time range
@app.command()
def main(
    project: Annotated[
        str, typer.Argument(..., help="The project name to filter the data.")
    ],
    start: Annotated[
        str, typer.Argument(..., help="The start date for the timesheet (YYYY-MM-DD).")
    ],
    end: Annotated[
        str, typer.Argument(..., help="The end date for the timesheet (YYYY-MM-DD).")
    ],
    output_path: Annotated[
        Path,
        typer.Option(
            "--output-path",
            "-o",
            help="The output path for the generated PDF file.",
        ),
    ] = Path.cwd(),
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            help="Print the version of the application.",
            callback=version_callback,
        ),
    ] = None,
):
    data = get_timew_data(project, start, end)
    generate_timesheet(data, output_path)


if __name__ == "__main__":
    app()
