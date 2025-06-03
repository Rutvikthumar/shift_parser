def export_to_csv(df):
    import os
    os.makedirs("output", exist_ok=True)
    df.to_csv("output/shifts.csv", index=False)

def export_to_gsheet(df):
    # TODO: Implement Google Sheets API export logic
    pass