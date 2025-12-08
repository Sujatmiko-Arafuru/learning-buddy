"""
Script untuk preprocessing data sebelum training
Tim ML dapat menggunakan script ini untuk mempersiapkan data dari MongoDB atau Excel
"""
import pandas as pd
import numpy as np
import os
import sys

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

from db import collections

def load_from_mongodb():
    """
    Load data dari MongoDB collections
    """
    print("Loading data from MongoDB...")
    
    data = {}
    
    # Load student progress
    if collections.get('student_progress'):
        progress = list(collections['student_progress'].find({}))
        data['student_progress'] = pd.DataFrame(progress)
        print(f"Loaded {len(progress)} student progress records")
    
    # Load courses
    if collections.get('courses'):
        courses = list(collections['courses'].find({}))
        data['courses'] = pd.DataFrame(courses)
        print(f"Loaded {len(courses)} courses")
    
    # Load learning paths
    if collections.get('learning_paths'):
        learning_paths = list(collections['learning_paths'].find({}))
        data['learning_paths'] = pd.DataFrame(learning_paths)
        print(f"Loaded {len(learning_paths)} learning paths")
    
    # Load skill keywords
    if collections.get('skill_keywords'):
        skill_keywords = list(collections['skill_keywords'].find({}))
        data['skill_keywords'] = pd.DataFrame(skill_keywords)
        print(f"Loaded {len(skill_keywords)} skill keywords")
    
    return data

def load_from_excel():
    """
    Load data dari file Excel di folder DATASET
    """
    print("Loading data from Excel files...")
    
    dataset_path = os.path.join(os.path.dirname(__file__), '../../DATASET')
    data = {}
    
    # Load LP and Course Mapping
    lp_course_file = os.path.join(dataset_path, 'LP and Course Mapping.xlsx')
    if os.path.exists(lp_course_file):
        # Read all sheets
        excel_file = pd.ExcelFile(lp_course_file)
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            data[sheet_name] = df
            print(f"Loaded sheet '{sheet_name}' with {len(df)} rows")
    
    # Load Resource Data
    resource_file = os.path.join(dataset_path, 'Resource Data Learning Buddy.xlsx')
    if os.path.exists(resource_file):
        excel_file = pd.ExcelFile(resource_file)
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            data[sheet_name] = df
            print(f"Loaded sheet '{sheet_name}' with {len(df)} rows")
    
    return data

def merge_data(data_dict):
    """
    Merge data dari berbagai sumber untuk training
    Tim ML dapat customize method ini sesuai kebutuhan
    """
    print("Merging data...")
    
    # Contoh: Merge student progress dengan courses
    if 'student_progress' in data_dict and 'courses' in data_dict:
        progress_df = data_dict['student_progress']
        courses_df = data_dict['courses']
        
        # Merge berdasarkan course_name atau course_id
        # merged = pd.merge(progress_df, courses_df, on='course_id', how='left')
        # return merged
    
    # Return first available dataframe
    if data_dict:
        return list(data_dict.values())[0]
    
    return pd.DataFrame()

def clean_data(df):
    """
    Clean data: handle missing values, outliers, etc.
    """
    print("Cleaning data...")
    
    cleaned_df = df.copy()
    
    # Handle missing values
    # cleaned_df = cleaned_df.dropna()  # atau fillna()
    
    # Remove duplicates
    cleaned_df = cleaned_df.drop_duplicates()
    
    # Handle outliers (jika diperlukan)
    # Q1 = cleaned_df.quantile(0.25)
    # Q3 = cleaned_df.quantile(0.75)
    # IQR = Q3 - Q1
    # cleaned_df = cleaned_df[~((cleaned_df < (Q1 - 1.5 * IQR)) | (cleaned_df > (Q3 + 1.5 * IQR))).any(axis=1)]
    
    print(f"Data cleaned: {len(cleaned_df)} rows remaining")
    return cleaned_df

def save_processed_data(df, filename='processed_data.csv'):
    """
    Save processed data ke folder data/processed
    """
    processed_path = os.path.join(os.path.dirname(__file__), '../data/processed')
    os.makedirs(processed_path, exist_ok=True)
    
    filepath = os.path.join(processed_path, filename)
    df.to_csv(filepath, index=False)
    print(f"Processed data saved to {filepath}")

def main():
    """
    Main preprocessing pipeline
    """
    print("=" * 50)
    print("Data Preprocessing Pipeline")
    print("=" * 50)
    
    # Option 1: Load from MongoDB
    data = load_from_mongodb()
    
    # Option 2: Load from Excel (uncomment jika perlu)
    # data = load_from_excel()
    
    if not data:
        print("No data loaded!")
        return
    
    # Merge data
    merged_data = merge_data(data)
    
    # Clean data
    cleaned_data = clean_data(merged_data)
    
    # Save processed data
    save_processed_data(cleaned_data)
    
    print("=" * 50)
    print("Preprocessing completed!")
    print("=" * 50)

if __name__ == '__main__':
    main()

