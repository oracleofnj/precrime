## app.R ##
library(shiny)
library(shinydashboard)
library(ggplot2)
library(dplyr)
library(leaflet)
library(geojsonio)

#data prepare
ts <- read.csv('../precrime_data/ts.csv')
ts2 <- read.csv('../precrime_data/ts2.csv')
ts3 <- read.csv('../precrime_data/ts3.csv')
ts_month <- read.csv('../precrime_data/ts_month.csv')

precincts <- geojsonio::geojson_read('../precrime_data/nypd_precincts.geojson', what='sp')

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
              h2("Raw Data"))
      
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
}

shinyApp(ui, server)