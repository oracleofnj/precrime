## app.R ##
library(shiny)
library(shinydashboard)
library(ggplot2)
library(dplyr)
library(leaflet)
library(geojsonio)
library("shiny")
library("shinydashboard")
library("highcharter")
library("dplyr")
library("viridisLite")
library("markdown")
library("quantmod")
library("tidyr")
library("DT")
library("shiny")
library("leaflet")
library("plotly")
library("wordcloud2")
library('scatterD3')
library(shiny)
library(leaflet)
library(data.table)
library(choroplethrZip)
library(devtools)
library(MASS)
library(vcd)
library(dplyr)
library(ggplot2)
library(tidyr)

library(readr)
library(viridis)
library(RColorBrewer)
library(gridExtra)

#data prepare
ts <- read.csv('/Users/panpancheng/Documents/study/capstone/Git/precrime/precrime_data/ts.csv')
ts2 <- read.csv('/Users/panpancheng/Documents/study/capstone/Git/precrime/precrime_data/ts2.csv')
ts3 <- read.csv('/Users/panpancheng/Documents/study/capstone/Git/precrime/precrime_data/ts3.csv')
ts_month <- read.csv('/Users/panpancheng/Documents/study/capstone/Git/precrime/precrime_data/ts_month.csv')



nypd <- read_csv("/Users/panpancheng/Documents/study/capstone/Git/precrime/precrime_data/clean_felonies.csv", col_types = cols(Date = col_date(format = "%m/%d/%Y"), Time = col_character()))
nypd$Year=format(nypd$COMPLAINT_DATETIME,"%Y")
nypd$Month=format(nypd$COMPLAINT_DATETIME,"%m")
nypd$Day=format(nypd$COMPLAINT_DATETIME,"%d")
nypd<-na.omit(nypd, cols=c('Longitude', 'Latitude'))

names(nypd)[names(nypd)=='Latitude']<-'lat'
names(nypd)[names(nypd)=='Longitude']<-'lng'
# Define server logic required to draw a histogram



precincts <- geojsonio::geojson_read('/Users/panpancheng/Documents/study/capstone/Git/precrime/precrime_data/nypd_precincts.geojson', what='sp')

bins <- c(2, 20, 50000, 70000, 100000, 120000, 140000, 180000, 250000)
pal <- colorBin(
  'viridis',
  domain=precincts$Population,
  bins=bins,
  reverse=T
)
highlight <- highlightOptions(
  weight = 5,
  color = "#666",
  dashArray = "",
  fillOpacity = 0.7,
  bringToFront = TRUE
)
labels <- sprintf(
  paste(
    "<strong>Precinct %d</strong><br/>",
    "Population: %s"
  ),
  as.integer(precincts$Precinct),
  format(as.integer(precincts$Population),big.mark=",", trim=TRUE)
) %>% lapply(htmltools::HTML)
labelopts <- labelOptions(
  style = list("font-weight" = "normal", padding = "3px 8px"),
  textsize = "15px",
  direction = "auto"
)




ui <- dashboardPage(
  dashboardHeader(title = "Crime Prediction"),
  dashboardSidebar(
    sidebarMenu(
      menuItem("Dashboard", tabName = "dashboard", icon = icon("dashboard")),        
      menuItem("Crime Map", tabName = "crimemap", icon = icon("map-marker")),
      menuItem("Population Map", tabName = "population", icon = icon("map-marker")),
      menuItem("Complaint Analysis", tabName = "complaint", icon = icon("bar-chart")),
      menuItem("Prediction", tabName = "prediction", icon = icon("area-chart")),
      menuItem("Raw data", tabName = "rawdata", icon = icon("table"))
    )
  ),
  dashboardBody(
    tabItems(
      tabItem(tabName = "dashboard",
              # Boxes need to be put in a row (or column)
              fluidRow(
                box(title = "Histogram of Total Crimes by Year",
                    status = "primary",
                    solidHeader = TRUE,
                    width = 12,
                    plotOutput("plot1"))),
              
              fluidRow(
                box(title = "Monthly Distribution of Crimes",
                    status = "primary",
                    solidHeader = TRUE,
                    width = 12,
                    plotOutput("plot4")))
              
      ),
      
      tabItem(tabName = "population",
              h2("Population Map"),
              
              box(
                title = "Population Map",
                collapsible = TRUE,
                width = "100%",
                height = "100%",
                leafletOutput("population_map")
              )),
      
      
      tabItem(tabName = "complaint",
              fluidRow(
                box(title = "Area Plot of Each Offense by Year",
                    status = "primary",
                    solidHeader = TRUE,
                    width = 12,
                    plotOutput("plot3"))
              ),
              
              fluidRow(
                box(title = "Area Plot of Each Borough by Year",
                    status = "primary",
                    solidHeader = TRUE,
                    width = 12,
                    plotOutput("plot2"))
              ),
              
              h2("Detailed Analysis")),
      
      tabItem(tabName = "prediction",
              h2("Crime Prediction")),
      
      tabItem(tabName = "rawdata",
              h2("Raw Data")),
      
      tabItem(tabName = "crimemap", 
              sidebarLayout(position = "right", 
                            sidebarPanel(
                              h4("Filter"),
                              
                              # widget for crime type
                              checkboxGroupInput("Crime_Type", label = "Crime_Type",
                                                 choices = c("BURGLARY", "FELONY ASSAULT", "GRAND LARCENY",
                                                             "GRAND LARCENY OF MOTOR VEHICLE", "RAPE", "ROBBERY",
                                                             "MURDER & NON-NEGL. MANSLAUGHTE"),
                                                 selected = c("BURGLARY", "FELONY ASSAULT", "GRAND LARCENY",
                                                              "GRAND LARCENY OF MOTOR VEHICLE", "RAPE","ROBBERY",
                                                              "MURDER & NON-NEGL. MANSLAUGHTE")),
                              
                              #date range
                              dateRangeInput("Date_Range", "Choose a date range", 
                                             start = "2016-10-01", end = "2016-12-31", 
                                             min = "2006-02-01", max = "2016-12-31"),
                              
                              
                              
                              h4("Click the Update button to see the map: "),
                              #update button
                              actionButton("button", "Update", 
                                           style="color: #fff; background-color: #337ab7; border-color: #2e6da4")
                            ),
                            
                            mainPanel(
                              leafletOutput("crimemap", width = "100%", height = 650)
                            )
              )
      )
      
    )
  ))

server <- function(input, output) {
  
  # Generate a plot of the requested variable against mpg and only 
  # include outliers if requested
  output$plot1 <- renderPlot({
    p <- ggplot(data=ts, aes(x=Year, y=Total_Crimes)) + geom_bar(stat='identity')
    print(p)
  })
  
  output$plot2 <- renderPlot({
    p <- ggplot(ts3, aes(x=Year,y=count1,group=BORO_NM,fill=BORO_NM)) + geom_area(position="stack")
    print(p)
  })
  
  output$plot3 <- renderPlot({
    p <- ggplot(ts2, aes(x=Year,y=count1,group=OFFENSE,fill=OFFENSE)) + geom_area(position="stack")
    print(p)
  })
  
  output$plot4 <- renderPlot({  
    p <- ggplot(ts_month)+geom_col(mapping=aes(Month,count1)) +ylab("Total Crimes")+ facet_wrap(~OFFENSE) +ggtitle("Monthly Distribution of Crimes") +theme(text = element_text(size=20), axis.text=element_text(size=10) )
    print(p)
  })
  
  
  
  output$population_map <- renderLeaflet({
    leaflet(precincts) %>% setView(-74,40.7,11) %>% addTiles() %>% addPolygons(
      fillColor = ~pal(Population),
      weight=2,
      opacity=1,
      color='white',
      dashArray='3',
      fillOpacity = 0.7,
      highlight=highlight,
      label=labels,
      labelOptions = labelopts
    )
  })
  
  
  
  
  #out map
  output$crimemap <- renderLeaflet({
    #### Map ######################################################################
    
    #read and update the input data
    start_date<-eventReactive(input$button, {
      start_date<-input$Date_Range[1]
    })
    
    end_date<-eventReactive(input$button, {
      input$button
      end_date<-input$Date_Range[2]
    })
    
    crime_type<-eventReactive(input$button, {
      input$button
      crime_type<-input$Crime_Type
    })
    
    # subsets the crime data depending on user input in the Shiny app
    filtered_crime_data <- eventReactive(input$button, {
      #filter by crime type,date range,hour
      filtered_crime_data<-nypd %>% 
        filter(as.Date(nypd$REPORT_DATE,origin = "1970-01-01") >= start_date() & 
                 as.Date(nypd$REPORT_DATE,origin = "1970-01-01") <= end_date())       %>%
        filter(OFNS_DESC %in% crime_type())
    })
    
    #set color
    col=c('darkred','yellow','cyan','deepskyblue','lightgreen','red','purple')
    
    #legend
    var=c( "BURGLARY", "FELONY ASSAULT", "GRAND LARCENY",
           "GRAND LARCENY OF MOTOR VEHICLE", "RAPE", "ROBBERY")
    
    #color palette
    pal <- colorFactor(col, domain = var)
    
    print(colnames(filtered_crime_data()))
    leaflet(data = filtered_crime_data()) %>% 
      addProviderTiles('Stamen.TonerLite') %>% 
      setView(lng = -73.971035, lat = 40.775659, zoom = 12) %>% 
      addCircles(lng=~lng, lat=~lat, radius=40, 
                 stroke=FALSE, fillOpacity=0.4,color=~pal(OFNS_DESC),
                 popup=~as.character(paste("Crime Type: ",OFNS_DESC,
                                           "Precinct: ",  ADDR_PCT_CD 
                 ))) %>%
      addLegend("bottomleft", pal = pal, values = ~OFNS_DESC,
                title = "Crime Type",
                opacity = 1 )%>% 
      addMarkers(
        clusterOptions = markerClusterOptions())
  })
  
  #### Theme #####################################################################
  hcbase <- reactive({
    
    hc <- highchart() 
    
    if (input$exporting)
      hc <- hc %>% hc_exporting(enabled = TRUE)
    if (input$theme != FALSE) {
      theme <- switch(input$theme,
                      null = hc_theme_null(),
                      economist = hc_theme_economist(),
                      dotabuff = hc_theme_db(),
                      darkunica = hc_theme_darkunica(),
                      gridlight = hc_theme_gridlight(),
                      sandsignika = hc_theme_sandsignika(),
                      fivethirtyeight = hc_theme_538(),
                      chalk = hc_theme_chalk(),
                      handdrwran = hc_theme_handdrawn()
      )
      
      hc <- hc %>% hc_add_theme(theme)
    }
    
    hc
    
  })
  
}

shinyApp(ui, server)