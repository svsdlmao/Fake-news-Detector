"""
Download and preprocess the LIAR dataset for fake news detection.
Expected: train.tsv, test.tsv, valid.tsv in data/ folder.
Download from: https://www.cs.ucsb.edu/~william/data/liar_dataset.zip
"""
import pandas as pd
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# LIAR dataset label mapping: group 6 labels into binary
FAKE_LABELS = {'pants-fire', 'false', 'barely-true'}
REAL_LABELS = {'true', 'mostly-true', 'half-true'}

def load_liar_tsv(filepath):
    """Load a LIAR dataset TSV file."""
    cols = ['id', 'label', 'statement', 'subject', 'speaker', 'speaker_job',
            'state', 'party', 'barely_true', 'false', 'half_true',
            'mostly_true', 'pants_on_fire', 'context']
    df = pd.read_csv(filepath, sep='\t', header=None, names=cols)
    return df

def preprocess(df):
    """Map 6-class labels to binary fake/real and clean text."""
    df = df[['statement', 'label']].copy()
    df = df.dropna(subset=['statement', 'label'])
    df['binary_label'] = df['label'].apply(
        lambda x: 'fake' if x in FAKE_LABELS else 'real' if x in REAL_LABELS else None
    )
    df = df.dropna(subset=['binary_label'])
    df = df[['statement', 'binary_label']].copy()
    df.columns = ['text', 'label']
    return df

def main():
    train_path = os.path.join(DATA_DIR, 'train.tsv')
    test_path = os.path.join(DATA_DIR, 'test.tsv')
    valid_path = os.path.join(DATA_DIR, 'valid.tsv')

    dfs = []
    for name, path in [('train', train_path), ('test', test_path), ('valid', valid_path)]:
        if os.path.exists(path):
            df = load_liar_tsv(path)
            df = preprocess(df)
            df['split'] = name
            dfs.append(df)
            print(f"{name}: {len(df)} samples")
            print(df['label'].value_counts())
            print()
        else:
            print(f"Warning: {path} not found. Download LIAR dataset first.")

    if dfs:
        combined = pd.concat(dfs, ignore_index=True)
        out_path = os.path.join(DATA_DIR, 'cleaned_dataset.csv')
        combined.to_csv(out_path, index=False)
        print(f"Saved cleaned dataset to {out_path}")
        print(f"Total samples: {len(combined)}")
        print(combined['label'].value_counts())
    else:
        print("No data files found. Please download the LIAR dataset:")
        print("https://www.cs.ucsb.edu/~william/data/liar_dataset.zip")
        print("Extract train.tsv, test.tsv, valid.tsv into the data/ folder.")

if __name__ == '__main__':
    main()
