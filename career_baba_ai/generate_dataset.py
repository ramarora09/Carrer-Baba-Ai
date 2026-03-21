import pandas as pd
data=[
    ["python sql excel", "Data Analyst"],
    ["python machine learning statistics", "Data Scientist"],
    ["java spring sql", "Backend Developer"],
    ["html css javascript react", "Frontend Developer"],
    ["python tensorflow deep learning", "ML Engineer"],
    ["aws docker kubernetes", "Cloud Engineer"],
    ["python pandas numpy", "Data Analyst"],
    ["javascript node mongodb", "Backend Developer"],
    ["html css javascript", "Frontend Developer"],
    ["python sklearn pandas", "Data Scientist"]
]
big_data=data *100
df=pd.DataFrame(big_data, columns=["skilss","role"])

df.to_csv("career_dataset.csv",index=False)
print("Dataset created successfully")