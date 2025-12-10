"""
Script to export entire MongoDB database to Excel file
Exports all collections to separate sheets in a single Excel file
"""
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from pymongo import MongoClient

# Add parent directory to path to import db module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import db

# Get DB_NAME from environment
load_dotenv()
DB_NAME = os.getenv('DB_NAME', 'learning_buddy_db')

def flatten_dict(d, parent_key='', sep='_'):
    """
    Flatten nested dictionary for Excel export
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert list to string representation
            if len(v) > 0:
                if isinstance(v[0], dict):
                    # List of dicts - convert to JSON string
                    items.append((new_key, json.dumps(v, ensure_ascii=False)))
                else:
                    # List of primitives - join with comma
                    items.append((new_key, ', '.join(str(x) for x in v)))
            else:
                items.append((new_key, ''))
        else:
            items.append((new_key, v))
    return dict(items)

def clean_value(value):
    """
    Clean value for Excel export
    """
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, default=str)
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)

def export_collection_to_dataframe(collection, collection_name, limit=None):
    """
    Export MongoDB collection to pandas DataFrame
    """
    print(f"  📥 Exporting {collection_name}...")
    
    try:
        # Get all documents
        query = {}
        if limit:
            cursor = collection.find(query).limit(limit)
        else:
            cursor = collection.find(query)
        
        docs = list(cursor)
        
        if not docs:
            print(f"    ⚠️  Collection '{collection_name}' is empty")
            return None
        
        print(f"    ✓ Found {len(docs)} documents")
        
        # Process documents
        processed_docs = []
        for doc in docs:
            # Remove _id (ObjectId) - convert to string if needed
            doc.pop('_id', None)
            
            # Flatten nested structures
            flat_doc = {}
            for key, value in doc.items():
                flat_doc[key] = clean_value(value)
            
            processed_docs.append(flat_doc)
        
        # Create DataFrame
        df = pd.DataFrame(processed_docs)
        
        # Limit columns if too many (Excel has 16,384 column limit)
        if len(df.columns) > 100:
            print(f"    ⚠️  Warning: {len(df.columns)} columns found, limiting to first 100")
            df = df.iloc[:, :100]
        
        return df
    
    except Exception as e:
        print(f"    ✗ Error exporting {collection_name}: {e}")
        return None

def export_database_to_excel(output_file='learning_buddy_database.xlsx', limit=None):
    """
    Export entire MongoDB database to Excel file
    Each collection becomes a separate sheet
    """
    if db is None:
        print("[ERROR] MongoDB connection failed")
        sys.exit(1)
    
    print("=" * 70)
    print("📊 MongoDB to Excel Export Tool")
    print("=" * 70)
    print(f"Database: {DB_NAME}")
    print(f"Output file: {output_file}")
    if limit:
        print(f"Limit: {limit} documents per collection")
    print("=" * 70)
    
    # Get all collection names
    collection_names = db.list_collection_names()
    
    if not collection_names:
        print("[ERROR] No collections found in database")
        sys.exit(1)
    
    print(f"\n📋 Found {len(collection_names)} collections:")
    for name in collection_names:
        print(f"  - {name}")
    
    # Create Excel writer
    print(f"\n📝 Creating Excel file: {output_file}")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        exported_count = 0
        skipped_count = 0
        
        for collection_name in collection_names:
            try:
                collection = db[collection_name]
                
                # Export collection to DataFrame
                df = export_collection_to_dataframe(collection, collection_name, limit=limit)
                
                if df is not None and not df.empty:
                    # Excel sheet name must be <= 31 characters and cannot contain: \ / ? * [ ]
                    sheet_name = collection_name[:31].replace('\\', '_').replace('/', '_').replace('?', '_').replace('*', '_').replace('[', '_').replace(']', '_')
                    
                    # Write to Excel sheet
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    exported_count += 1
                    print(f"    ✅ Exported to sheet: {sheet_name}")
                else:
                    skipped_count += 1
                    print(f"    ⏭️  Skipped (empty or error)")
            
            except Exception as e:
                print(f"    ✗ Error processing {collection_name}: {e}")
                skipped_count += 1
                continue
        
        # Create summary sheet
        summary_data = {
            'Collection Name': collection_names,
            'Status': ['Exported' if name in [db.list_collection_names()[i] for i in range(exported_count)] else 'Skipped' for name in collection_names]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    print("\n" + "=" * 70)
    print("✅ Export completed!")
    print("=" * 70)
    print(f"📊 Collections exported: {exported_count}")
    print(f"⏭️  Collections skipped: {skipped_count}")
    print(f"📁 Output file: {os.path.abspath(output_file)}")
    print("=" * 70)
    
    return output_file

def main():
    """
    Main function
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Export MongoDB database to Excel')
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='learning_buddy_database.xlsx',
        help='Output Excel file name (default: learning_buddy_database.xlsx)'
    )
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=None,
        help='Limit number of documents per collection (default: no limit)'
    )
    
    args = parser.parse_args()
    
    # Generate filename with timestamp if not specified
    if args.output == 'learning_buddy_database.xlsx':
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f'learning_buddy_database_{timestamp}.xlsx'
    
    try:
        output_file = export_database_to_excel(args.output, limit=args.limit)
        print(f"\n🎉 Success! Database exported to: {output_file}")
        print("\n💡 Tip: You can upload this file to Google Drive or GitHub for sharing.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

