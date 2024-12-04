# Generate Timesheet

## Assumptions

This *script* assumes use of *Taskwarrior* and *Timewarrior* in conjunction with the *Taskwarrior* provided `on-modify.timewarrior` hook. 

This hook extract the project, the task title and any tags of a task as tags to a *Timewarrior* entry whenever you start a task. 

## Usage

```
> generate-timesheet --project <PROJECT> --start <STARTDATE> --end <ENDDATE>
```