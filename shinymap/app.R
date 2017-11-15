## app.R ##
library(shiny)
library(shinydashboard)
library(ggplot2)
library(dplyr)


ui <- dashboardPage(
  dashboardHeader(title = "Crime Prediction"),
  dashboardSidebar(
    sidebarMenu(
      menuItem("Dashboard", tabName = "dashboard", icon = icon("dashboard")),        
      menuItem("Crime Map", tabName = "crimemap", icon = icon("map-marker")),
      menuItem("Subway Allocation", tabName = "subway", icon = icon("bar-chart")),
      menuItem("School Absence Analysis", tabName = "school", icon = icon("bar-chart")),
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
      box(title = "Area Plot of Each Borough by Year",
          status = "primary",
          solidHeader = TRUE,
          width = 12,
          plotOutput("plot2")))),
    
    tabItem(tabName = "crimemap",
            h2("Crime Map")),
    
    tabItem(tabName = "subway",
            h2("Subway Allocation And Crime")),
    
    tabItem(tabName = "school",
            h2("School Absense And Crime")),
    
    tabItem(tabName = "complaint",
            fluidRow(
              box(title = "Area Plot of Each Offense by Year",
                  status = "primary",
                  solidHeader = TRUE,
                  width = 12,
                  plotOutput("plot3"))),
            h2("Detailed Analysis")),
    
    tabItem(tabName = "prediction",
            h2("Crime Prediction")),
    
    tabItem(tabName = "rawdata",
            h2("Raw Data"))
    
)
))

server <- function(input, output) {
  
  nypd <- read.csv('clean_felonies.csv')
  nypd$COMPLAINT_DATETIME=as.POSIXct(nypd$COMPLAINT_DATETIME)
  nypd$Year = format(nypd$COMPLAINT_DATETIME, '%Y')
  ts <- nypd %>% group_by(Year) %>% summarise(Total_Crimes=n())
  
  nypd_offense <- read.csv('clean_felonies_offense.csv')
  nypd_offense$COMPLAINT_DATETIME=as.POSIXct(nypd_offense$COMPLAINT_DATETIME)
  nypd_offense$Year = format(nypd_offense$COMPLAINT_DATETIME, '%Y')
  ts2 <- nypd_offense %>% group_by(Year,OFFENSE) %>% summarise(count1=n())
  
  ts3 <- nypd_offense %>% group_by(Year,BORO_NM) %>% summarise(count1=n())
  
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
  
}

shinyApp(ui, server)