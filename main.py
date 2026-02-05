import argparse
import pandas as pd


COLS_QUALIFICATION = [
        # Keys
        'order_id', 'patient_globalentryid', 'report_identifier', 'report_version',
    
        # Socioeconomic factors for patient health
        'patientdata_education', 'patientdata_workingstatus', 'patientdata_unemployment',
        'patientdata_economicinactivity', 'patientdata_homeless', 
        'patientdata_partofaminority', 'patientdata_withdisabilities',
    
        # Occupational risks concerning patient health
        'patientcard_environmentalrisks_miner', 'patientcard_environmentalrisks_ironmillworker',
        'patientcard_environmentalrisks_constructionworker', 'patientcard_environmentalrisks_welder',
        'patientcard_environmentalrisks_stonemason', 'patientcard_environmentalrisks_railwayman',
        'patientcard_environmentalrisks_roadworker', 'patientcard_environmentalrisks_carpenter',
        'patientcard_environmentalrisks_firefighter', 'patientcard_environmentalrisks_professionaldriver',
    
        # Smoking metrics
        'patientcard_packyears_packyearsvalue', 'patientcard_packyears_yearssmoking',
        'patientcard_packyears_avgpacksaday', 'patientcard_smokingstatus',
        'patientcard_currentcessationperiod', 'patientcard_attemptstoquit',
    
        # Pulmonary cancer symptoms
        'patientcard_pulmonarycancersymptoms_persistentcough', 
        'patientcard_pulmonarycancersymptoms_chestpains',
        'patientcard_pulmonarycancersymptoms_hoarseness',
        'patientcard_pulmonarycancersymptoms_weightloss',
        'patientcard_pulmonarycancersymptoms_coughingblood',
        'patientcard_pulmonarycancersymptoms_dyspnea',
    
        # Surveys
        'addictsurvey_nightwakeforcigarette', 'addictsurvey_firstmorningcigarette',
        'motivationsurvey_doyouwanttoquit'
]

COLS_NDTK = [
        # Keys & metadata
        'order_id', 'id', 'patient_globalentryid', 'report_version', 'reportdate',
        'physician_officialid',
    
        # General findings
        'nodules_totalnodulesnumber',
        'nodules_lymphnodes_lymphnodes',
        'emphysema_emphysema',
        'emphysema_coronarycalcifications',
    
        # Conclusions
        'nodules_noduleslist_action',
        'impression_impression_nodules',
        'impression_impressionotherfindings',
        'followup_followup',
    
        # Technical scan data?
        #'scaninformations_scanslicethickness_reconstructedslicethickness',
        #'scaninformations_scanexamtype'
]

COLS_RESULT = [
        # Keys
        'order_id', 'id', 'report_version',

        # Time & physician responsible
        'reportdate', 'physician_officialid',

        # Meeting details
        'explained_symptoms',
        'explained_tobacco_smoking_risks',

        # Next steps
        'followup0',
        'informed_about_need_for_pulmonary_test',
        'informed_about_need_for_next_screening',
        'informed_about_need_for_other_test'
]


def load_to_df_and_fuse(kwalifikacyjne, NDTK, wynikowe):
        # df_komplet = pd.read_csv(args.all_tests)
        try:
                df_kwalifikacyjne = pd.read_csv(kwalifikacyjne, usecols=COLS_QUALIFICATION, dtype=str)
        except ValueError as e:
                print(f"ERROR: Column mismatch in Qualification file. {e}")
                return None
        try:
                df_NDTK = pd.read_csv(NDTK, usecols=COLS_NDTK, dtype=str)
        except ValueError as e:
                print(f"ERROR: Column mismatch in NDTK file. {e}")
                return None

        try:
                df_wynikowe = pd.read_csv(wynikowe, usecols=COLS_RESULT, dtype=str)
        except ValueError as e:
                print(f"ERROR: Column mismatch in Results file. {e}")
                return None

        df_patient_profile = pd.merge(
        df_kwalifikacyjne, 
        df_NDTK, 
        on='order_id', 
        how='left'
        )
        
        df_patient_profile = pd.merge(
        df_patient_profile,
        df_wynikowe,
        on='order_id',
        how='left'
        )
        
        return df_patient_profile


if __name__ == "__main__":

        parser = argparse.ArgumentParser

        # parser.add_argument(
        #       '-a', '--all_tests', 
        #       required=True, 
        #       help="Path to the summary test .csv file"
        #)

        parser.add_argument(
                '-q', '--qualification', 
                required=True, 
                help="Path to the qualification results .csv file"
        )

        parser.add_argument(
                '-n', '--ndtk',
                required=True,
                help="Path to the NDTK results .csv file"
        )

        parser.add_argument(
                '-r', '--results',
                required=True,
                help="Path to the total results of the medical tests .csv file"
        )

        parser.add_argument(
                '-o', '--output',
                default="output_database.csv",
                help="Output filename"
        )

        args = parser.parse_args()

        final_df = load_to_df_and_fuse(args.qualification, args.ndtk, args.results)

        print(f"\nSaving to {args.output}: ")
        final_df.to_csv(args.output, index=False, na_rep = 'Brak danych', sep=';') # conversion of achieved DataFrame into a .csv file
        print("CSV created successfully.")