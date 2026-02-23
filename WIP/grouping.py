import pandas as pd

filepath = (R"data\Metadane - opisy NDTK (rpt_ndtk_reports).csv")

try:
    df_NDTK = pd.read_csv(filepath, dtype=str)
except FileNotFoundError:
    print("File not found.")


# NDTK_short = df_NDTK.iloc[:20]
df_NDTK = df_NDTK.sort_values(by=['reportdate'], )

NDTK_grouped = (df_NDTK.groupby('patient_globalentryid')
    .agg({"reportdate": list,
         "report_title": list,
         "report_items_0_items_0_value":list,
         "nodules_noduleslist_nodulnumber": list,
         "nodules_noduleslist_spiculated": list,
        "nodules_noduleslist_smoothedges": list,
        "nodules_noduleslist_calcifications": list,
        "nodules_noduleslist_isitnew": list,
        "nodules_noduleslist_endobronchial_endobronchial": list,
        "nodules_noduleslist_noduleconsistency": list,
        "nodules_noduleslist_nodulelength": list,
        "nodules_noduleslist_lungsegment_lungsegment": list,
        "nodules_noduleslist_lungsegment_lungsegmentright": list,
        "nodules_noduleslist_lungsegment_lungsegmentleft": list,
        "nodules_noduleslist_action": list,
        "nodules_noduleslist_volume": list,
        "nodules_noduleslist_indexnodule": list,
        "nodules_noduleslist_arraypath": list,
        "nodules_lymphnodes_lymphnodes": list,
        "nodules_totalnodulesnumber": list,
        "scaninformations_scanslicethickness_reconstructedslicethickness": list,
        "scaninformations_scanexamtype": list,
        "emphysema_emphysema": list,
        "emphysema_coronarycalcifications": list,
        "impression_impression_nodules": list,
        "impression_impressionotherfindings": list,
        "impression_impressionremarks": list, 
        "followup_followup": list, 
})
)

print(NDTK_grouped)