import sys, pandas as pd, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

df_raw = pd.read_csv("files/input/solicitudes_de_credito.csv", sep=";", index_col=0)

expected = [990,483,423,383,376,372,361,348,328,308,270,255,255,247,234,232,231,202,174,170,169,124,117,115,114,90,89,89,86,85,78,72,70,67,65,59,55,52,50,49,48,48,48,47,45,44,43,43,43,40,38,37,36,36,34,34,33,33,32,30,27,27,27,26,26,25,25,24,24,24,24,23,21,21,21,20,20,20,20,17,17,17,16,14,14,14,14,13,13,12,11,11,11,11,10,10,10,9,9,9,9,8,8,8,8,8,8,7,7,7,7,7,7,7,6,6,6,6,6,6,6,6,6,6,6,6,5,5,5,5,5,5,4,4,4,4,4,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]

def clean_col(s):
    s = s.astype(str).str.lower()
    s = s.str.replace("_"," ").str.replace("-"," ")
    s = s.apply(lambda x: unicodedata.normalize("NFKD",x).encode("ascii","ignore").decode("utf-8"))
    return s.str.replace(r"\s+"," ",regex=True).str.strip()

def run(df_in, dedup_order="after"):
    df = df_in.copy()
    df.dropna(inplace=True)
    df.columns = ["sexo","tipo_de_emprendimiento","idea_negocio","barrio","estrato","comuna_ciudadano","fecha_de_beneficio","monto_del_credito","linea_credito"]
    
    if dedup_order == "before":
        df.drop_duplicates(inplace=True)
    
    for col in ["sexo","tipo_de_emprendimiento","idea_negocio","barrio","linea_credito"]:
        df[col] = clean_col(df[col])
    
    df["monto_del_credito"] = df["monto_del_credito"].astype(str).str.replace(r"[$,]","",regex=True).str.strip().astype(float).astype(int)
    f = pd.to_datetime(df["fecha_de_beneficio"].astype(str), dayfirst=True, errors="coerce")
    m = f.isna(); f[m] = pd.to_datetime(df["fecha_de_beneficio"].astype(str)[m], dayfirst=False, errors="coerce")
    df["fecha_de_beneficio"] = f.dt.strftime("%Y-%m-%d")
    df["estrato"] = df["estrato"].astype(int)
    df["comuna_ciudadano"] = df["comuna_ciudadano"].astype(float).astype(int)
    
    if dedup_order == "after":
        df.drop_duplicates(inplace=True)
    elif dedup_order == "both":
        df.drop_duplicates(inplace=True)
    
    vc = df["barrio"].value_counts().to_list()
    match = vc == expected
    print(f"dedup={dedup_order}: {len(df)} rows, {len(vc)} barrios, sexo={df['sexo'].value_counts().to_list()}, barrio_match={match}")
    if not match and len(vc) > 220:
        for i,(a,e) in enumerate(zip(vc, expected)):
            if a != e:
                print(f"  first diff idx={i}: ours={a}, expected={e}")
                break
    return df

run(df_raw, "before")
run(df_raw, "after")
run(df_raw, "both")
