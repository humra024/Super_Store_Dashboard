# setup virtual environment-
# open folder in vscode, 
# python3 -m venv .venv
# ok
# kill the server, compile again to enter virtual Environmen
# install all the libraries then import

import pandas as pd 
import streamlit as st 
import plotly.express as px 
import os 
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore!", page_icon=":bar_chart", layout="wide")
st.title(" :bar_chart: Sample Superstpre EDA")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
else:
    # os.chdir(r"C:\Users\AEPAC\Desktop\Streamlit")
    df = pd.read_csv("Superstore.csv", encoding = "ISO-8859-1")
    
    
col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"]) #converting column to date time format

# Getting the min and max date (start and end date from data)
startDate = pd.to_datetime(df["Order Date"]).min()
# or   startDate = df["Order Date"].min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1: #start date (can also be selected) else min taken
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2: #end date (can also be selected) else max taken
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

#filtering dates between start and end date
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()


#sidebar
st.sidebar.header("Choose your filter: ")


# Create for Region
region = st.sidebar.multiselect("Pick the Region", df["Region"].unique())
if not region: #if no region selected the all the regions i.e. no filtering
    df2 = df.copy() #df2 created for state
else:
    df2 = df[df["Region"].isin(region)] #filtering acc to region
    
#Create for State
state=st.sidebar.multiselect("Pick the State", df2['State'].unique()) #states in selected region 
if not state:
    df3=df2.copy() #df3 created for city
else:
    df3=df2[df2["State"].isin(state)] #state filter applied on region filtered date df2

#Create for City
city=st.sidebar.multiselect("Pick the City", df3['City'].unique()) #cities in selected state
#df4 not created as this is the final data selected, after this city data is not used for further down selection

# Filter the data based on Region, State and City

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df[df["State"].isin(state) & df["City"].isin(city)]
elif region and city:
    filtered_df = df[df["Region"].isin(region) & df["City"].isin(city)]
elif region and state:
    filtered_df = df[df["Region"].isin(region) & df["State"].isin(state)]
elif city:
    filtered_df = df[df["City"].isin(city)]
else:
    filtered_df = df[df["Region"].isin(region) & df["State"].isin(state) & df3["City"].isin(city)]

category_df = filtered_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x = "Category", y = "Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values = "Sales", names = "Region", hole = 0.5)
    fig.update_traces(text = filtered_df["Region"], textposition = "outside") #region text appear outside
    st.plotly_chart(fig,use_container_width=True)
    
    
    # ====== 
    
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by = "Region", as_index = False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv",
                        help = 'Click here to download the data as a CSV file')
        
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="Sales", labels = {"Sales": "Amount"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of TimeSeries:"):
                      #transpose:T
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')

# Create a treem based on Region, category, sub-Category
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path = ["Region","Category","Sub-Category"], values = "Sales",hover_data = ["Sales"],
                  color = "Sub-Category")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values = "Sales", names = "Segment", template = "plotly_dark")
    fig.update_traces(text = filtered_df["Segment"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values = "Sales", names = "Category", template = "gridon")
    fig.update_traces(text = filtered_df["Category"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region","State","City","Category","Sales","Profit","Quantity"]]
    fig = ff.create_table(df_sample, colorscale = "Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data = filtered_df, values = "Sales", index = ["Sub-Category"],columns = "month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# Create a scatter plot
data1 = px.scatter(filtered_df, x = "Sales", y = "Profit", size = "Quantity")
data1['layout'].update(title="Relationship between Sales and Profits using Scatter Plot.",
                       titlefont = dict(size=20),xaxis = dict(title="Sales",titlefont=dict(size=19)),
                       yaxis = dict(title = "Profit", titlefont = dict(size=19)))
st.plotly_chart(data1,use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))

# ========

st.subheader("3D Scatter Plot")
    
xa = st.selectbox(
    'x axis',
    ('Category','Region', 'Sales','Profit', 'Quantity'))
ya = st.selectbox(
    'y axis',
    ('Category','Region', 'Sales','Profit', 'Quantity'))
za = st.selectbox(
    'z axis',
    ('Category','Region', 'Sales','Profit', 'Quantity'))

    
fig = px.scatter_3d(filtered_df, x=xa, y=ya, z=za,
              color=xa)
st.plotly_chart(fig,use_container_width=True)



