from ms_sql_handler import ms_sql_handler
import pandas as pd
import cx_Oracle as co
import reader
import datetime
from other import add_cols
import json

class demographics_import():

    def __init__(self,cache_path) : #0
        #here need to import json file
        #and used that to store
        demo_cahce= reader.read_json(cache_path+"/data/demographics.json")
        for item in [*demo_cahce] :
            setattr(self,item, demo_cahce[item])
        #and import metric data needed
        self.df_hsn = pd.read_json(cache_path+"/data/sample_metrics.json")
        #df2['year']=df2['year'].astype(int)
        for df_column in self.df_hsn.columns:
            self.df_hsn[df_column]=self.df_hsn[df_column].astype(int)

        
        
    
    def get_lims_demographics(self,hsn): #1
        #HSN_WGSRUNDATE_INDEX_
        date= hsn[0].split("_")[1]
        self.wgs_run_date = date
     
        #making sure only HSN and cutting other stuff in the array
        hsn = [i.split("_")[0] for i in hsn]
   
        #self.df_hsn = pd.DataFrame(hsn,columns=["hsn"]) #<-could be defined else where, 
        #this will need be a variable i m thinking a jason file that will also feed into msql class
        conn = co.connect(self.lims_connection)

        query="select * from wgsdemographics where HSN in ("+",".join(hsn)+")"

        self.lims_df = pd.read_sql(query,conn)
        print("current lims output")
        print(self.lims_df.to_string())
        conn.close()
    
    def format_lims_df(self): #2
        # manipulate sql database to format accepted by the master EXCEL worksheet
        #self.log.write_log("format_lims_DF","Manipulating demographics to database format")
        self.lims_df = self.lims_df.rename(columns = self.demo_names)
        self.lims_df["hsn"] = self.lims_df.apply(lambda row: str(row["hsn"]), axis=1)
        #self.log.write_log("format_lims_DF","Done!")


    def merge_dfs(self): #3
        #self.log.write_log("merge_dfs","Merging dataframes")
        self.lims_df['hsn']=self.lims_df['hsn'].astype(int)
      
        self.df = pd.merge(self.lims_df, self.df_hsn, how="inner", on="hsn")
 
       #              self.log.write_log("merge_dfs","Done")
    
    def format_dfs(self): #3 

        #self.log.write_log("format_dfs","Starting")
        # format columns, insert necessary values
        #self.log.write_log("format_dfs","Adding/Formatting/Sorting columns")

        self.df = add_cols(obj=self, \
            df=self.df, \
            col_lst=self.add_col_lst, \
            col_func_map=self.col_func_map)

        # sort/remove columns to match list
        self.df = self.df[self.sample_data_col_order]


        #self.log.write_log("format_dfs","Done")
    
    def database_push(self): #4
        #self.log.write_log("database_push","Starting")
        self.setup_db()
        df_demo_lst = self.df.values.astype(str).tolist()
       
        #df_table_col_query = "(" + ", ".join(self.df.columns.astype(str).tolist()) + ")"
        
        self.write_query_tbl1 = (" ").join(self.write_query_tbl1)
   
        self.db_handler.lst_ptr_push(df_lst=df_demo_lst, query=self.write_query_tbl1)
        #self.log.write_log("database_push","Done!`")

    def setup_db(self):
        self.db_handler = ms_sql_handler(self)
        self.db_handler.establish_db()
    



        