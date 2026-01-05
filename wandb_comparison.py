#!/usr/bin/env python3
"""
W&B Comparison Script for GitHub Actions
Fetches baseline run and creates a comparison report with the specified run.
"""

import os
import sys
import wandb
from typing import Optional


def get_baseline_run(api: wandb.Api, entity: str, project: str) -> Optional[wandb.apis.public.Run]:
    """
    Fetch the run tagged as 'baseline' in the W&B project.
    
    Args:
        api: W&B API instance
        entity: W&B entity (username or team)
        project: W&B project name
        
    Returns:
        The baseline run if found, None otherwise
    """
    try:
        runs = api.runs(f"{entity}/{project}", filters={"tags": {"$in": ["baseline"]}})
        baseline_run = next(runs, None)
        
        if baseline_run is None:
            print("Error: No run found with tag 'baseline'")
            return None
            
        print(f"Found baseline run: {baseline_run.id} ({baseline_run.name})")
        return baseline_run
    except Exception as e:
        print(f"Error fetching baseline run: {e}")
        return None


def get_run_by_id(api: wandb.Api, entity: str, project: str, run_id: str) -> Optional[wandb.apis.public.Run]:
    """
    Fetch a specific run by its ID.
    
    Args:
        api: W&B API instance
        entity: W&B entity (username or team)
        project: W&B project name
        run_id: The run ID to fetch
        
    Returns:
        The run if found, None otherwise
    """
    try:
        run = api.run(f"{entity}/{project}/{run_id}")
        print(f"Found run: {run.id} ({run.name})")
        return run
    except Exception as e:
        print(f"Error fetching run {run_id}: {e}")
        return None


def create_comparison_report(
    api: wandb.Api,
    entity: str,
    project: str,
    baseline_run: wandb.apis.public.Run,
    comparison_run: wandb.apis.public.Run
) -> Optional[str]:
    """
    Create a comparison URL between baseline and comparison run.
    Uses W&B's built-in compare feature which provides a direct comparison view.
    
    Args:
        api: W&B API instance
        entity: W&B entity (username or team)
        project: W&B project name
        baseline_run: The baseline run
        comparison_run: The run to compare against baseline
        
    Returns:
        URL to the comparison view, or None if creation failed
    """
    try:
        # Use W&B's built-in compare feature
        # Format: https://wandb.ai/{entity}/{project}/compare?run={run1}&run={run2}
        compare_url = f"https://wandb.ai/{entity}/{project}/compare?run={baseline_run.id}&run={comparison_run.id}"
        print(f"Created comparison URL: {compare_url}")
        return compare_url
    except Exception as e:
        print(f"Error creating comparison URL: {e}")
        return None


def main():
    """Main function to orchestrate the comparison process."""
    # Get environment variables
    wandb_api_key = os.getenv("WANDB_API_KEY")
    entity = os.getenv("WANDB_ENTITY")
    project = os.getenv("WANDB_PROJECT")
    run_id = os.getenv("RUN_ID")
    
    # Validate required environment variables
    if not wandb_api_key:
        print("Error: WANDB_API_KEY environment variable not set")
        sys.exit(1)
    if not entity:
        print("Error: WANDB_ENTITY environment variable not set")
        sys.exit(1)
    if not project:
        print("Error: WANDB_PROJECT environment variable not set")
        sys.exit(1)
    if not run_id:
        print("Error: RUN_ID environment variable not set")
        sys.exit(1)
    
    # Initialize W&B API
    wandb.login(key=wandb_api_key)
    api = wandb.Api()
    
    print(f"Entity: {entity}, Project: {project}, Run ID: {run_id}")
    
    # Fetch baseline run
    print("\nFetching baseline run...")
    baseline_run = get_baseline_run(api, entity, project)
    if baseline_run is None:
        print("Failed to fetch baseline run")
        sys.exit(1)
    
    # Fetch comparison run
    print(f"\nFetching comparison run: {run_id}...")
    comparison_run = get_run_by_id(api, entity, project, run_id)
    if comparison_run is None:
        print(f"Failed to fetch run {run_id}")
        sys.exit(1)
    
    # Create comparison report
    print("\nCreating comparison report...")
    report_url = create_comparison_report(api, entity, project, baseline_run, comparison_run)
    
    if report_url is None:
        print("Failed to create comparison report")
        sys.exit(1)
    
    print(f"\n✅ Success! Comparison report URL: {report_url}")
    
    # Write URL to file for GitHub Actions to read
    with open("report_url.txt", "w") as f:
        f.write(report_url)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
