
import pandas as pd
import matplotlib.pyplot as plt


class Plant_Eval():
    def __init__(self,load_csv,name):
        
        self.plant_eval_load_data = load_csv
        self.plant_eval_name = name
        self.plant_eval_clean_load = pd.DataFrame()
        self.plant_eval_ETB_data = pd.DataFrame()
        
    def plant_eval_data_cleanup(self):
        self.plant_eval_load_data['Time'] = pd.to_datetime(self.plant_eval_load_data['Time'])
        start_date = self.plant_eval_load_data['Time'].min()
        end_date = self.plant_eval_load_data['Time'].max()
        complete_range = pd.date_range(start=start_date, end=end_date, freq='30T')
        complete_df = pd.DataFrame({'complete_time': complete_range})
        self.plant_eval_clean_load = pd.merge(complete_df, self.plant_eval_load_data, how='left', left_on='complete_time', right_on='Time')
        self.plant_eval_clean_load.to_csv("Plant_Eval_Clean_Data.csv")
        return self.plant_eval_clean_load
        
    def get_key_metrics(self):
        plt.plot(range(1,len(self.plant_eval_clean_load)+1),self.plant_eval_clean_load['Psum_kW'])
        plt.title(self.plant_eval_name)
        plt.ylabel("Power Consumption in KW")
        plt.xlabel("Time interval in 30 mins")
        plt.grid()
        return
    
    def plant_ETB_data(self):
        self.plant_eval_ETB_data = self.plant_eval_data_cleanup()
        average = self.plant_eval_ETB_data.mean(numeric_only=True)
        self.plant_eval_ETB_data.fillna(average)
        self.plant_eval_ETB_data.to_csv("Plant_Eval_ETB_Data.csv")
        
    def get_max_power(self):
        return self.plant_eval_ETB_data['Psum_kW'].max()*1.25
    
    def plant_Eval_Analytics(self):
        df = self.plant_eval_ETB_data
        df["x_points"] = range(1,len(df)+1)
        plt.subplot(4,1,1)
        plt.title(self.plant_eval_name + " Load profile")
        plt.ylabel("Line currents in Amps")
        plt.xlabel("Time intervals in 1 second")
        plt.plot(df["x_points"],df["I1"], label = "Line Current A")
        plt.plot(df["x_points"],df["I2"], label = "Line Current B")
        plt.plot(df["x_points"],df["I3"], label = "Line Current C")
        plt.grid()
        plt.legend()
        
        plt.subplot(4,1,2)
        plt.ylabel("Line voltages in [V]")
        plt.xlabel("Time intervals in 1 second")
        plt.plot(df["x_points"],df["V12"],label = "Line-to-line V12")
        plt.plot(df["x_points"],df["V23"], label = "Line-to-line V23")
        plt.plot(df["x_points"],df["V31"], label = "Line-to-line V31")
        plt.grid()
        plt.legend()
        
        plt.subplot(4,1,3)
        plt.xlabel("Time interval in 30 mins")
        plt.ylabel("Power consumpotion in KW")
        plt.grid()
        plt.plot(df['x_points'],df['Psum_kW'],label = 'Original data from logger')
        plt.legend()
        
        plt.subplot(4,1,4)
        plt.xlabel("Time interval in 30 mins")
        plt.ylabel("Power factor p.u")
        plt.grid()
        plt.plot(df["x_points"],df["PF1"],label = "PF1")
        plt.plot(df["x_points"],df["PF2"], label = "PF2")
        plt.plot(df["x_points"],df["PF3"], label = "PF3")
        plt.legend()
        return
    
class System_Builder(Plant_Eval):
    def __init__(self,load_csv,name,hours,distance):
        super().__init__(load_csv, name)
        self.Hybrid_install_rate = 1.05
        self.markup = 1/0.85
        self.default_string_length = 100
        self.Bat_hours = hours
        self.distance_to_site = distance
        self.Battery_list = pd.read_excel("inventory_spec.xlsx",sheet_name="BATTERIES")
        self.Inverter_list = pd.read_excel("inventory_spec.xlsx",sheet_name="HYBRID INVERTERS")
        self.PV_list = pd.read_excel("inventory_spec.xlsx",sheet_name="PV")    
        self.Car_specifications = pd.read_excel("inventory_spec.xlsx",sheet_name="Logistics")
        self.DC_switch_gear = pd.read_excel("inventory_spec.xlsx",sheet_name = "DC Protection Box")
        self.AC_switch_gear = pd.read_excel("inventory_spec.xlsx",sheet_name = "AC Switch Gear")
        return

    def get_battery_spec(self):
        self.plant_eval_data_cleanup()
        self.plant_ETB_data()
        column_sizes = self.Battery_list.loc[:, 'Energy']
        available_sizes = column_sizes.tolist()
        selected_size = None
        min_difference = float('inf')
        
        

        for size in available_sizes:
            if size >= self.get_max_power()*self.Bat_hours*1/0.800: 
                difference = abs(self.get_max_power()*self.Bat_hours*1/0.800 - size)
                if difference < min_difference:
                    min_difference = difference
                    selected_size = size
                    
        selected_row = self.Battery_list[self.Battery_list['Energy']==selected_size].iloc[0]

        
        return  selected_size

    def get_inverter_spec(self):
        self.plant_eval_data_cleanup()
        self.plant_ETB_data()
        column_sizes = self.Inverter_list.loc[:, 'Rated power']
        available_sizes = column_sizes.tolist()
        selected_size = None
        min_difference = float('inf')
        
        

        for size in available_sizes:
            if size >= self.get_max_power()/0.750: 
                difference = abs(self.get_max_power()/0.750 - size)
                if difference < min_difference:
                    min_difference = difference
                    selected_size = size
                    
        selected_row = self.Inverter_list[self.Inverter_list['Rated power']==selected_size].iloc[0]
        
        return  selected_size
    def get_selected_battery(self):
        self.plant_eval_data_cleanup()
        self.plant_ETB_data()
        column_sizes = self.Battery_list.loc[:, 'Energy']
        available_sizes = column_sizes.tolist()
        selected_size = None
        min_difference = float('inf')
        
        

        for size in available_sizes:
            if size >= self.get_max_power()*self.Bat_hours*1/0.800: 
                difference = abs(self.get_max_power()*self.Bat_hours*1/0.800 - size)
                if difference < min_difference:
                    min_difference = difference
                    selected_size = size
                    
        selected_row = self.Battery_list[self.Battery_list['Energy']==selected_size].iloc[0]

        
        return  selected_row

    def get_selected_inverter(self):
        self.plant_eval_data_cleanup()
        self.plant_ETB_data()
        column_sizes = self.Inverter_list.loc[:, 'Rated power']
        available_sizes = column_sizes.tolist()
        selected_size = None
        min_difference = float('inf')
        
        

        for size in available_sizes:
            if size >= self.get_max_power()/0.750: 
                difference = abs(self.get_max_power()/0.750 - size)
                if difference < min_difference:
                    min_difference = difference
                    selected_size = size
                    
        selected_row = self.Inverter_list[self.Inverter_list['Rated power']==selected_size].iloc[0]

        return  selected_row

        
    def get_grid_tied_inv_spec(self):
        Number_of_Grid_tied_inverters = int(self.get_PV_size()/100)
        if Number_of_Grid_tied_inverters == 0:
            return 1
        else:
            return Number_of_Grid_tied_inverters
        pass
    
# =============================================================================
#     PV Size calculator :
#   inputs : Max plant load and battery size to calculate the required PV 
#   PV sized to charge the battery in 4 hours and supply load during daytime conditions
# =============================================================================
    def get_PV_size(self):
        self.plant_eval_data_cleanup()
        self.plant_ETB_data()
        PV_Kwp = self.get_max_power()*1000 + self.get_battery_spec()*1000/4
        return PV_Kwp/1000
  
    def get_Panels(self):
        self.plant_eval_data_cleanup()
        self.plant_ETB_data()
        PV_Kwp = self.get_max_power()*1000 + self.get_battery_spec()*1000/4
        return int(PV_Kwp/550 )
    
    def logistics_and_Accoodation(self):
        Total_days = self.get_total_install_days()
        distance = self.get_distance_to_site()*2
        day_rate = 75
        Acc_rate = 200
        return Total_days*(distance*18+day_rate + Acc_rate)
        
    def Installation_and_Commisioning(self):
        modules_to_be_installed = self.get_Panels()
        total_dc_capacity = int(self.get_Panels()*550+1)
        installation_panels_per_day = 50
        standing_unforseen_delays = 0.15 #15 percent
        Total_days_required_for_module_installation=modules_to_be_installed/installation_panels_per_day*(1+standing_unforseen_delays)
        
        foreman_rate = 150 #per hour
        Inverter_rate = 150 #per Hour
        install_team  = 8 # 4 members per team
        working_hours = 9 #Working hours
        Person_per_team  = 6 #Size of installation team
        electricians = 5 
        Foreman = 1
        PV_installer_rate = 120
        modeule_intstaller_rate = Total_days_required_for_module_installation*(Foreman*foreman_rate+PV_installer_rate*electricians)*working_hours
        inverter_installer_rate = 2.21*(Foreman*foreman_rate+PV_installer_rate*electricians)*working_hours
        install_Commisioning_cost = modeule_intstaller_rate+inverter_installer_rate
       
        
        return install_Commisioning_cost
        
    def get_total_install_days(self):
        modules_to_be_installed = self.get_Panels()
        total_dc_capacity = int(self.get_Panels()*550+1)
        installation_panels_per_day = 50
        standing_unforseen_delays = 0.15 #15 percent
        Total_days_required_for_module_installation=modules_to_be_installed/installation_panels_per_day*(1+standing_unforseen_delays)
        return Total_days_required_for_module_installation
    
    def Scaffold_access_and_rigging(self):
        ladder_day_rate = 500
        Forklift_day_rate = 300
        
        return (self.get_total_install_days()*(ladder_day_rate+Forklift_day_rate))
        
    def Cable_racking_and_trunking(self,ac_cable_tray,dc_cable_tray):
        return ac_cable_tray * 2200 + dc_cable_tray *1600
        
        pass
     
    def get_distance_to_site(self):
        return self.distance_to_site
     
    
    def Quote_printOut(self):
        import openpyxl
        self.plant_eval_data_cleanup()
        self.plant_ETB_data()
        # Load the Excel workbook
        workbook = openpyxl.load_workbook('Quote_template.xlsx')
        
        sheet = workbook['Quote']
        
        cell_to_edit = sheet['D15'] 
        cell_to_edit.value = self.plant_eval_name
        
        #Installation and Commisioning cell
        cell_to_edit = sheet['H32'] 
        cell_to_edit.value = self.Installation_and_Commisioning()*self.markup
        cell_to_edit = sheet['G32'] 
        cell_to_edit.value = 1
        cell_to_edit = sheet['F32'] 
        cell_to_edit.value = self.Installation_and_Commisioning()*self.markup

        #PV Price cell 
        cell_to_edit = sheet['G22'] 
        cell_to_edit.value = self.get_Panels()
        cell_to_edit = sheet['H22'] 
        cell_to_edit.value = self.get_Panels()*550*2.80*self.markup
        cell_to_edit = sheet['F22'] 
        cell_to_edit.value = 550*2.80*self.markup
        
        #Logistics and Accomodation
        cell_to_edit = sheet['H36'] 
        cell_to_edit.value = self.logistics_and_Accoodation()*self.markup
        cell_to_edit = sheet['G36'] 
        cell_to_edit.value = 1
        cell_to_edit = sheet['F36'] 
        cell_to_edit.value = self.logistics_and_Accoodation()*self.markup

        #Engineering detail design and signoff
        cell_to_edit = sheet['H35'] 
        cell_to_edit.value = 24000*self.markup
        cell_to_edit = sheet['G35'] 
        cell_to_edit.value = 1
        cell_to_edit = sheet['F35'] 
        cell_to_edit.value =24000*self.markup
        
        #PV arrangement and structure
        cell_to_edit = sheet['H35'] 
        cell_to_edit.value = 24000*self.markup
        cell_to_edit = sheet['G35'] 
        cell_to_edit.value = 1
        cell_to_edit = sheet['F35'] 
        cell_to_edit.value =24000*self.markup
        
        #Battery arrangement and structure
        battery_specs = self.get_selected_battery()
        cell_to_edit = sheet['H24'] 
        cell_to_edit.value = battery_specs["Price"]*self.markup
        cell_to_edit = sheet['G24'] 
        cell_to_edit.value = 1
        cell_to_edit = sheet['F24'] 
        cell_to_edit.value =battery_specs["Price"]*self.markup

        
        #PV arrangement and structure
        cell_to_edit = sheet['H25'] 
        cell_to_edit.value = self.get_Panels()*550*self.Hybrid_install_rate*self.markup
        cell_to_edit = sheet['G25'] 
        cell_to_edit.value = 1
        cell_to_edit = sheet['F25'] 
        cell_to_edit.value =self.get_Panels()*550*self.Hybrid_install_rate*self.markup  
        
        #AC and DC cable Ladder
        cell_to_edit = sheet['H26'] 
        cell_to_edit.value = self.Cable_racking_and_trunking(20, 150)*self.markup
        cell_to_edit = sheet['G26'] 
        cell_to_edit.value = 1
        cell_to_edit = sheet['F26'] 
        cell_to_edit.value =self.Cable_racking_and_trunking(20, 150)*self.markup
        
        
        #Scaffold_acces and rigging
        cell_to_edit = sheet['H33'] 
        cell_to_edit.value = self.Scaffold_access_and_rigging()*self.markup
        cell_to_edit = sheet['G33'] 
        cell_to_edit.value = 1
        cell_to_edit = sheet['F33'] 
        cell_to_edit.value =self.Scaffold_access_and_rigging()*self.markup
        
        #DC Protection Box
        cell_to_edit = sheet['H27'] 
        cell_to_edit.value = self.DC_protection()*self.markup
        cell_to_edit = sheet['G27'] 
        cell_to_edit.value = 1
        cell_to_edit = sheet['F27'] 
        cell_to_edit.value =self.DC_protection()*self.markup
        
        
        #DC Cable calculatiojn
        cell_to_edit = sheet['H28'] 
        cell_to_edit.value = self.DC_cable()*self.markup
        cell_to_edit = sheet['G28'] 
        cell_to_edit.value = 1
        cell_to_edit = sheet['F28'] 
        cell_to_edit.value =self.DC_cable()*self.markup
        
        #AC Switcgear calculatiojn
        cell_to_edit = sheet['H29'] 
        cell_to_edit.value = self.AC_switch()*self.markup
        cell_to_edit = sheet['G29'] 
        cell_to_edit.value = 1
        cell_to_edit = sheet['F29'] 
        cell_to_edit.value =self.AC_switch()*self.markup
        
        
        #Earth wire and consumables
        cell_to_edit = sheet['H30'] 
        cell_to_edit.value = self.Earth_Cable_Consumables()*self.markup
        cell_to_edit = sheet['G30'] 
        cell_to_edit.value = 1
        cell_to_edit = sheet['F30'] 
        cell_to_edit.value =self.Earth_Cable_Consumables()*self.markup
        
        #Inverter section
        inv_sel=self.get_selected_inverter()

        cell_to_edit = sheet['H23'] 
        cell_to_edit.value = (inv_sel["Price"]+self.get_grid_tied_inv_spec()*73000)*self.markup
        cell_to_edit = sheet['G23'] 
        cell_to_edit.value = 1
        cell_to_edit = sheet['F23'] 
        cell_to_edit.value =(inv_sel["Price"]+self.get_grid_tied_inv_spec()*73000)*self.markup
        
        workbook.save(self.plant_eval_name+'.xlsx')
        workbook.close()
        

    def DC_cable(self):
        panels_per_string = 18
        length_per_string = self.default_string_length
        number_of_strings = self.get_Panels()/panels_per_string
        price_per_meter = 16.87
        return number_of_strings*2*price_per_meter*length_per_string
        
        
    def Earth_Cable_Consumables(self):
        Earth_wire = 200 *33 
        Saddles = 100 * 5
        Earth_spikes = 4*360
        Earth_plate = 8 
        return Earth_plate*Earth_wire+Saddles+Earth_spikes
    
    def DC_protection(self):
        selected_inverter = self.get_selected_inverter()
        power_rating = selected_inverter["Rated power"]/selected_inverter["Inverter_num"]
        #selected_row = self.Inverter_list[self.Inverter_list['Rated power']==selected_size].iloc[0]
        inv_dc_protection = self.DC_switch_gear[self.DC_switch_gear["Rated power"]==power_rating].iloc[0]
        print(inv_dc_protection)
        return selected_inverter["Inverter_num"]*inv_dc_protection["Price"]    
    def AC_switch(self):
        selected_inverter = self.get_selected_inverter()
        power_rating = selected_inverter["Rated power"]/selected_inverter["Inverter_num"]
        #selected_row = self.Inverter_list[self.Inverter_list['Rated power']==selected_size].iloc[0]
        inv_ac_protection = self.AC_switch_gear[self.AC_switch_gear["Rated power"]==power_rating].iloc[0]
        return selected_inverter["Inverter_num"]*inv_ac_protection["Price"]
        
    def get_cable_dimensions(self):
        pass
    def output_system(self):
        pass

def main():
    plant_eval_tester()
    
    return


def plant_eval_tester():
    
    df = pd.read_csv("load_incoming.csv")
    plant = System_Builder(df,"Broadway Sweets", hours=4,distance = 60)
    plant.plant_eval_data_cleanup()
    plant.get_key_metrics()
    plant.plant_eval_data_cleanup()
    plant.plant_ETB_data()
    plant.plant_Eval_Analytics()
    
    plant.get_inverter_spec()
    plant.get_battery_spec()
    plant.get_Panels()
    plant.get_grid_tied_inv_spec()
    plant.logistics_and_Accoodation()
    plant.Installation_and_Commisioning()
    plant.DC_protection()
    plant.Quote_printOut()
    return

if __name__ == "__main__":
    main()