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

nypd <- read_csv("../precrime_data/clean_felonies_offense.csv", col_types = cols(Date = col_date(format = "%m/%d/%Y"), Time = col_character()))
#nypd$OFFENSE<-nypd$OFNS_DESC
nypd$Year=format(nypd$COMPLAINT_DATETIME,"%Y")
nypd$Month=format(nypd$COMPLAINT_DATETIME,"%m")
nypd$Day=format(nypd$COMPLAINT_DATETIME,"%d")
nypd<-na.omit(nypd, cols=c('Longitude', 'Latitude'))
pred_17<-read_csv("../model_predictions/2016/final_2017_predictions.csv")
pred_17$date<-as.Date(with(pred_17, paste(COMPLAINT_YEAR, COMPLAINT_MONTH, COMPLAINT_DAY,sep="-")), "%Y-%m-%d")
pred_17$All<-pred_17$Arson + pred_17$Burglary + 
  pred_17$CriminalMischief + pred_17$Drugs + pred_17$FelonyAssault + 
  pred_17$Forgery + pred_17$Fraud + pred_17$GrandLarceny + 
  pred_17$GrandLarcenyAuto + pred_17$Homicide + pred_17$Rape + pred_17$Robbery + 
  pred_17$Weapons + pred_17$Other
ts <- nypd %>% group_by(Year) %>% summarise(Total_Crimes=n())
ts2 <- nypd %>% group_by(OFFENSE,Year) %>% summarise(count1=n())
ts_month <- nypd %>% group_by(OFFENSE,Month) %>% summarise(count1=n())
ts3 <- nypd %>% group_by(Year,BORO_NM) %>% summarise(count1=n())

names(nypd)[names(nypd)=='Latitude']<-'lat'
names(nypd)[names(nypd)=='Longitude']<-'lng'


Crime_Per_Month <- ts_month
# Define server logic required to draw a histogram



precincts <- geojsonio::geojson_read('../precrime_data/nypd_precincts.geojson', what='sp')


precincts_pred<-precincts



ui <- dashboardPage(
  dashboardHeader(title = "Crime Prediction"),
  dashboardSidebar(
    sidebarMenu(
      menuItem("Crime Map", tabName = "crime", icon = icon("map-marker")),
      menuItem("Time Series Analysis", tabName = "dashboard", icon = icon("dashboard")),  
      #menuItem("Population Map", tabName = "population", icon = icon("map-marker")),
      menuItem("Complaint Analysis", tabName = "complaint", icon = icon("bar-chart")),
      menuItem("Prediction", tabName = "prediction", icon = icon("map-marker")),
      menuItem("Report data", tabName = "rawdata", icon = icon("table"))
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
                leafletOutput("population_map",height=670)
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
              #h2("Crime Map"),
              
              box(
                #title = "Crime Map",
                collapsible = TRUE,
                width = "100%",
                height = "100%",
                leafletOutput("predictionmap",height=670),
                absolutePanel(top = 10, right = 10,
                              # widget for crime type
                              selectInput("Crime_Type_pred", 
                                          label = "Crime Type",
                                          choices = c("Arson", "Burglary","CriminalMischief","Drugs","FelonyAssault","Forgery","Fraud","GrandLarceny","GrandLarcenyAuto","Homicide","Rape","Robbery", "Weapons" ,"Other", "All" ),
                                          selected = "All"
                              ),
                              
                              #date range
                              dateRangeInput("Date_Range_pred", "Choose a Date Range", 
                                             start = "2017-01-01", end = "2017-01-31", 
                                             min = "2017-01-01", max = "2017-12-31"),
                              sliderInput("Time_Range_pred", "Choose a Time Range", 
                                          #start = "2017-10-01", end = "2017-1-31", 
                                          min = 0, max = 24, value=c(0,24))
                              
                              #update button
                              #actionButton("button", "Go", 
                              #             style="color: #fff; background-color: #337ab7; border-color: #2e6da4")
                )
                
              )),
      
      tabItem(tabName = "rawdata",
              #h2("Crime Amount Per Month Data"),
              fluidPage(
                
                # App title ----
                titlePanel("Downloading Data"),
                
                # Sidebar layout with input and output definitions ----
                sidebarLayout(
                  
                  # Sidebar panel for inputs ----
                  sidebarPanel(
                    
                    # Input: Choose dataset ----
                    selectInput("dataset", "Choose a dataset:",
                                choices = c("Crime_Per_Month","Crime_Per_Year")),
                    
                    # Button
                    downloadButton("downloadData", "Download")
                    
                  ),
                  
                  # Main panel for displaying outputs ----
                  mainPanel(
                    
                    tableOutput("table")
                    
                  )
                  
                )
              )
      ),
      
      tabItem(tabName = "crime",
              #h2("Crime Map"),
              
              box(
                #title = "Crime Map",
                collapsible = TRUE,
                width = "100%",
                height = "100%",
                leafletOutput("crimemap",height=670),
                absolutePanel(top = 10, right = 10,
                              # widget for crime type
                              selectInput("Crime_Type", 
                                          label = "Crime Type",
                                          choices = c("Arson", "Burglary","CriminalMischief","Drugs","FelonyAssault","Forgery","Fraud","GrandLarceny","GrandLarcenyAuto","Homicide","Rape","Robbery", "Weapons" ,"Other" ),
                                          selected = c("Arson", "Burglary","CriminalMischief","Drugs","FelonyAssault","Forgery","Fraud","GrandLarceny","GrandLarcenyAuto","Homicide","Rape","Robbery", "Weapons" ,"Other" )
                              ),
                              
                              #date range
                              dateRangeInput("Date_Range", "Choose a Date Range", 
                                             start = "2016-10-01", end = "2016-12-31", 
                                             min = "2006-01-02", max = "2016-12-31")
                              
                              #update button
                              #actionButton("button", "Go", 
                              #             style="color: #fff; background-color: #337ab7; border-color: #2e6da4")
                )
                
              ))
      
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
    start_date<-reactive({input$Date_Range[1]
    })
    
    end_date<-reactive({input$Date_Range[2]
    })
    
    crime_type<-reactive({crime_type<-input$Crime_Type
    })
    
    # subsets the crime data depending on user input in the Shiny app
    filtered_crime_data <- reactive({nypd %>% 
        filter(as.Date(nypd$REPORT_DATE,origin = "1970-01-01") >= start_date() & 
                 as.Date(nypd$REPORT_DATE,origin = "1970-01-01") <= end_date())       %>%
        filter(OFFENSE %in% crime_type())
    })
    ####################
    nypd1<-nypd %>% 
      filter(as.Date(nypd$REPORT_DATE,origin = "1970-01-01") >= input$Date_Range[1] & 
               as.Date(nypd$REPORT_DATE,origin = "1970-01-01") <= input$Date_Range[2])       %>%
      filter(OFFENSE %in% input$Crime_Type)
    # take the subset of nypd data according to crime and date range
    l<-nypd1 %>%
      group_by(ADDR_PCT_CD) %>% 
      summarise(freq=n())
    l$Precinct<-l$ADDR_PCT_CD
    # merge with the spatial data frame of precincts
    precincts@data<-merge(precincts@data,l, by='Precinct', all.x=T, all.y=T,sort=T)
    
    months<-as.double(difftime(input$Date_Range[2],input$Date_Range[1],units = 'days'))/30
    precincts@data$months=months
    
    # set the population of central park to 1000 for smoother gradation
    index<-precincts@data$Precinct==22
    
    precincts@data$Population[index]=1000
    
    print(precincts@data$Population)
    
    precincts@data$freq[is.na(precincts@data$freq)] <- 0
    
    # data modification for plotting
    precincts@data['pop_by_100k']<-precincts@data['Population']/100000
    precincts@data['v1']<- precincts@data['freq']/ precincts@data['pop_by_100k']
    precincts@data['value']<- precincts@data['v1']/ precincts@data['months']
    print(precincts@data)
    
    ###################
    #set color
    col=c('honeydew','lightblue','hotpink','lightgoldenrodyellow','ivory','gray91','lemonchiffon1','darkred','yellow','cyan','deepskyblue','lightgreen','red','purple')
    
    #legend
    var=c("Arson", "Burglary","CriminalMischief","Drugs","FelonyAssault","Forgery","Fraud","GrandLarceny","GrandLarcenyAuto","Homicide","Rape","Robbery", "Weapons" ,"Other" )
    
    #color palette
    pal <- colorFactor(col, domain = var)
    ######## map options
    bins <- seq(min(precincts@data$value),max(precincts@data$value),length.out=10)
    pal_1 <- colorBin(
      'viridis',
      domain=precincts$value,
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
    print(colnames(filtered_crime_data()))
    
    
    ####widget
    leaflet(data = filtered_crime_data()) %>% 
      addProviderTiles('Stamen.TonerLite') %>% 
      setView(lng = -73.971035, lat = 40.775659, zoom = 12) %>% 
      addPolygons(data=precincts,
                  fillColor = ~pal_1(precincts$value),
                  weight=2,
                  opacity=1,
                  color='white',
                  dashArray='3',
                  fillOpacity = 0.7,
                  highlight=highlight,
                  label=labels,
                  labelOptions = labelopts
      )%>%
      #addCircles(lng=~lng, lat=~lat, radius=40, 
      # stroke=FALSE, fillOpacity=0.4,color=~pal(OFFENSE),
      #popup=~as.character(paste("Crime Type: ",OFFENSE,
      #                         "Precinct: ",  ADDR_PCT_CD 
      #))) %>%
      leaflet::addLegend("bottomleft", pal = pal_1, values = precincts$value,
                         title = "crime per month per 100k pop",
                         opacity = 1 )%>%
      addMarkers(
        clusterOptions = markerClusterOptions())
  })
  #out map
  output$predictionmap <- renderLeaflet({
    
    #### Map ######################################################################
    
    #read and update the input data
    start_date<-reactive({input$Date_Range_pred[1]
    })
    
    end_date<-reactive({input$Date_Range_pred[2]
    })
    
    crime_type<-reactive({crime_type<-input$Crime_Type_pred
    })
    
    start_time<-reactive({input$Time_Range_pred[1]
    })
    end_time<-reactive({input$Time_Range_pred[2]
    })
    print(input$Time_Range_pred[1])
    print(input$Time_Range_pred[2])
    # subsets the crime data depending on user input in the Shiny app
    filtered_pred_data <- reactive({pred_17 %>% 
        filter(as.Date(pred_17$date,origin = "1970-01-01") >= start_date() & 
                 as.Date(pred_17$date,origin = "1970-01-01") <= end_date())      # %>%
        #filter(pred_17$COMPLAINT_HOURGROUP>=start_time() &
                 #pred_17$COMPLAINT_HOURGROUP<=end_time() )
      
    })
    ####################
    pred_17_1<-pred_17 %>% 
      filter(as.Date(pred_17$date,origin = "1970-01-01") >= as.Date(input$Date_Range_pred[1]) & 
               as.Date(pred_17$date,origin = "1970-01-01") <= as.Date(input$Date_Range_pred[2]) )      #%>%
      #filter(as.numeric(pred_17$COMPLAINT_HOURGROUP)>=input$Time_Range_pred[1] &
               #as.numeric(pred_17$COMPLAINT_HOURGROUP)<=input$Time_Range_pred[2] )
    # take the subset of nypd data according to crime and date range
    print(pred_17_1)
    l_pred<-pred_17_1 %>%
      group_by(ADDR_PCT_CD) %>% 
      summarise_all(funs(sum))
    l_pred<-data.frame(l_pred)
    l_pred$Precinct<-l_pred$ADDR_PCT_CD
    print(input$Date_Range_pred[1])
          print(input$Date_Range_pred[2])
    print(l_pred)
    # merge with the spatial data frame of precincts
    
    precincts_pred@data<-merge(precincts_pred@data,l_pred, by='Precinct', all.x=T, all.y=T,sort=T)
    
    months_pred<-as.double(difftime(input$Date_Range_pred[2],input$Date_Range_pred[1],units = 'days'))/30
    precincts_pred@data$months=months_pred
    hours_pred<-months_pred*((input$Time_Range_pred[2]-input$Time_Range_pred[1])/4)
    precincts_pred@data$hours=hours_pred
    # set the population of central park to 1000 for smoother gradation
    index_pred<-precincts_pred@data$Precinct==22
    
    precincts_pred@data$Population[index_pred]=10000
    
    #print(precincts_pred@data$Population)
    
    precincts_pred@data[[input$Crime_Type]][is.na(precincts_pred[input$Crime_Type_pred])] <- 0
    
    # data modification for plotting
    precincts_pred@data['pop_by_100k']<-precincts_pred@data['Population']/100000
    precincts_pred@data['v1']<- precincts_pred@data[input$Crime_Type]/ precincts_pred@data['pop_by_100k']
    precincts_pred@data['value']<- precincts_pred@data['v1']/ precincts_pred@data['hours']
    #print(precincts_pred@data)
    
    ###################
    #set color
    col=c('honeydew','lightblue','hotpink','lightgoldenrodyellow','ivory','gray91','lemonchiffon1','darkred','yellow','cyan','deepskyblue','lightgreen','red','purple', 'blue')
    
    #legend
    var=c("Arson", "Burglary","CriminalMischief","Drugs","FelonyAssault","Forgery","Fraud","GrandLarceny","GrandLarcenyAuto","Homicide","Rape","Robbery", "Weapons" ,"Other", "All" )
    
    #color palette
    pal <- colorFactor(col, domain = var)
    #print(precincts_pred@data)
    ######## map options
    bins <- seq(min(precincts_pred@data$value),max(precincts_pred@data$value),length.out=10)
    pal_1 <- colorBin(
      'viridis',
      domain=precincts$value,
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
      as.integer(precincts_pred$Precinct),
      format(as.integer(precincts_pred$Population),big.mark=",", trim=TRUE)
    ) %>% lapply(htmltools::HTML)
    labelopts <- labelOptions(
      style = list("font-weight" = "normal", padding = "3px 8px"),
      textsize = "15px",
      direction = "auto"
    )
    print(colnames(filtered_pred_data()))
    

    ####widget
    leaflet(data = precincts_pred) %>% 
      addProviderTiles('Stamen.TonerLite') %>% 
      setView(lng = -73.971035, lat = 40.775659, zoom = 12) %>% 
      addPolygons(
                  fillColor = ~pal_1(precincts_pred$value),
                  weight=2,
                  opacity=1,
                  color='white',
                  dashArray='3',
                  fillOpacity = 0.7,
                  highlight=highlight,
                  label=labels,
                  labelOptions = labelopts
      )%>%
      #addCircles(lng=~lng, lat=~lat, radius=40, 
      # stroke=FALSE, fillOpacity=0.4,color=~pal(OFFENSE),
      #popup=~as.character(paste("Crime Type: ",OFFENSE,
      #                         "Precinct: ",  ADDR_PCT_CD 
      #))) %>%
      leaflet::addLegend("bottomleft", pal = pal_1, values = precincts_pred$value,
                         title = "crime per 4 hours per 100k pop",
                         opacity = 1 )#%>%
      #addMarkers(
        #clusterOptions = markerClusterOptions())
  })
  #########raw data###########
  # Reactive value for selected dataset ----
  datasetInput <- reactive({
    switch(input$dataset,
           "Crime_Per_Month" = Crime_Per_Month,
           "Crime_Per_Year" = ts2)
  })
  
  # Table of selected dataset ----
  output$table <- renderTable({
    datasetInput()
  })
  
  # Downloadable csv of selected dataset ----
  output$downloadData <- downloadHandler(
    filename = function() {
      paste(input$dataset, ".csv", sep = "")
    },
    content = function(file) {
      write.csv(datasetInput(), file, row.names = FALSE)
    }
  )
  
}

shinyApp(ui, server)
