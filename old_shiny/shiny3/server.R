#
# This is the server logic of a Shiny web application. You can run the 
# application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
# 
#    http://shiny.rstudio.com/
#

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

nypd <- read_csv("../precrime_data/clean_felonies.csv", col_types = cols(Date = col_date(format = "%m/%d/%Y"), Time = col_character()))
nypd$Year=format(nypd$COMPLAINT_DATETIME,"%Y")
nypd$Month=format(nypd$COMPLAINT_DATETIME,"%m")
nypd$Day=format(nypd$COMPLAINT_DATETIME,"%d")
nypd<-na.omit(nypd, cols=c('Longitude', 'Latitude'))

names(nypd)[names(nypd)=='Latitude']<-'lat'
names(nypd)[names(nypd)=='Longitude']<-'lng'
# Define server logic required to draw a histogram

function(input, output) {
  
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
  
  #out map
  output$map <- renderLeaflet({
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
  
  ################################################################################  
  
  
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