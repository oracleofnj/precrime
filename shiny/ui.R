#
# This is the user-interface definition of a Shiny web application. You can
# run the application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
# 
#    http://shiny.rstudio.com/
#
###########################
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

##########################
library(shiny)

# Define UI for application that draws a histogram
shinyUI(
  dashboardPage(
    skin = "black",
    dashboardHeader(title = "Crime Prediction", disable = FALSE),
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
        ################################################################################################   time series part           
        tabItem(tabName = "dashboard",
                fluidRow(
                  column(4, selectInput("theme", label = "Theme",
                                        choices = c(FALSE, "fivethirtyeight", "economist", "dotabuff",
                                                    "darkunica", "gridlight",
                                                    "sandsignika", "null", "handdrwran",
                                                    "chalk"))),
                  column(4, selectInput("exporting", label = "Exporting enabled", choices = c(FALSE, TRUE)))
                  
                ),
                box(width = 10, highchartOutput("highstock")),
                box(width = 2, title = "Filter",
                    checkboxGroupInput("Crimetype", label = "Crime Type: ",
                                       choices = c('Arson',
                                                   'Weapons', 'Fraud', 'GrandLarceny', 'Robbery', 'Burglary', 'Homicide', 'Drugs', 'Rape',
                                                   'GrandLarcenyAuto', 'CriminalMischief', 'FelonyAssault', 'Forgery', 'Other'),
                                       selected =c('Arson',
                                                   'Weapons', 'Fraud', 'GrandLarceny', 'Robbery', 'Burglary', 'Homicide', 'Drugs', 'Rape',
                                                   'GrandLarcenyAuto', 'CriminalMischief', 'FelonyAssault', 'Forgery', 'Other')), 
                    actionButton("button2", "Update", 
                                 style="color: #fff; background-color: #337ab7; border-color: #2e6da4")), 
                box(width = 12, highchartOutput("highheatmap")),
                fluidRow(
                  column(4, selectInput("ct", label = "Crime Type: ",
                                        choices = c('Arson',
                                                    'Weapons', 'Fraud', 'GrandLarceny', 'Robbery', 'Burglary', 'Homicide', 'Drugs', 'Rape',
                                                    'GrandLarcenyAuto', 'CriminalMischief', 'FelonyAssault', 'Forgery', 'Other'))), 
                  column(4, sliderInput("ci", label = "Confidence Interval%: ", min = 0, 
                                        max = 99, value = c(80, 95)))
                ), 
                box(width = 12, plotOutput("forecast"))
                
        ),
        ################################################################################################ crime map
        tabItem(tabName = "crimemap", 
                sidebarLayout(position = "right", 
                              sidebarPanel(
                                h4("Filter"),
                                
                                # widget for crime type
                                checkboxGroupInput("Crime_Type", label = "Crime_Type",
                                                   choices = c('Arson',
                                                               'Weapons', 'Fraud', 'GrandLarceny', 'Robbery', 'Burglary', 'Homicide', 'Drugs', 'Rape',
                                                               'GrandLarcenyAuto', 'CriminalMischief', 'FelonyAssault', 'Forgery', 'Other'),
                                                   selected = c('Arson',
                                                                'Weapons', 'Fraud', 'GrandLarceny', 'Robbery', 'Burglary', 'Homicide', 'Drugs', 'Rape',
                                                                'GrandLarcenyAuto', 'CriminalMischief', 'FelonyAssault', 'Forgery', 'Other')),
                                
                                #date range
                                dateRangeInput("Date_Range", "Choose a date range", 
                                               start = "2015-10-01", end = "2015-12-31", 
                                               min = "2000-01-01", max = "2015-12-31"),
                                
                                #start and end hour
                                sliderInput("IntHour", "Start time", 0, 23, 0, step = 1),
                                sliderInput("EndHour", "End time", 0, 23, 23, step = 1),
                                
                                h4("Click the Update button to see the map: "),
                                #update button
                                actionButton("button", "Update", 
                                             style="color: #fff; background-color: #337ab7; border-color: #2e6da4")
                              ),
                              
                              mainPanel(
                                leafletOutput("map", width = "100%", height = 650)
                              )
                )
        ), 
        
        ################################################################################################   public facility part           
        tabItem(tabName = "subway",
                absolutePanel(
                  bottom = 120, right = 30, width = 300,
                  height = "auto",draggable = TRUE, 
                  wellPanel(
                    HTML(markdownToHTML(fragment.only=TRUE, text=c(
                      "PUBLIC FACILITY: Hospital, Government, Factory, etc.",
                      "ENTERTAINMENT: Theater, Recreational Facility, Hotel, etc.",
                      "RESIDENTIAL AREA: Apartment, Condo, etc."
                    )))
                  ),
                  style = "opacity: 0.92"
                ),
                sidebarLayout(position = "right", 
                              sidebarPanel(
                                h4("Filter"),
                                
                                # widget for facility type
                                selectInput("Facility_Category", label = "Facility Category",
                                            choices = c("PUBLIC FACILITY", 
                                                        "ENTERTAINMENT", 
                                                        "RESIDENTIAL AREA",
                                                        "RESTAURANT/CAFE", 
                                                        "BAR"),
                                            selected = "Public Facility (Government Office, Schools, Hospital, Stores and Warehouse, etc.)"),
                                
                                # widget for crime type
                                checkboxGroupInput("p_Crime_Type", label = "Crime_Type",
                                                   choices = c('Arson',
                                                               'Weapons', 'Fraud', 'GrandLarceny', 'Robbery', 'Burglary', 'Homicide', 'Drugs', 'Rape',
                                                               'GrandLarcenyAuto', 'CriminalMischief', 'FelonyAssault', 'Forgery', 'Other'),
                                                   selected = c('Arson',
                                                                'Weapons', 'Fraud', 'GrandLarceny', 'Robbery', 'Burglary', 'Homicide', 'Drugs', 'Rape',
                                                                'GrandLarcenyAuto', 'CriminalMischief', 'FelonyAssault', 'Forgery', 'Other'))
                              ),
                              mainPanel(
                                tabsetPanel(
                                  tabPanel("Summary", highchartOutput("facilitymap1", width = "100%", height = 650)), 
                                  tabPanel("Plot",plotOutput("facilitymap2", width = "100%", height = 700))
                                )
                                #plotOutput("facilitymap", width = "100%", height = 700)
                              ))
        ),
        ################################################################################################ crime map
        tabItem(tabName = "school", 
                sidebarLayout(position = "right", 
                              sidebarPanel(
                                h4("Filter"),
                                
                                # widget for crime type
                                checkboxGroupInput("Crime_Type", label = "Crime_Type",
                                                   choices = c('Arson',
                                                               'Weapons', 'Fraud', 'GrandLarceny', 'Robbery', 'Burglary', 'Homicide', 'Drugs', 'Rape',
                                                               'GrandLarcenyAuto', 'CriminalMischief', 'FelonyAssault', 'Forgery', 'Other'),
                                                   selected = c('Arson',
                                                                'Weapons', 'Fraud', 'GrandLarceny', 'Robbery', 'Burglary', 'Homicide', 'Drugs', 'Rape',
                                                                'GrandLarcenyAuto', 'CriminalMischief', 'FelonyAssault', 'Forgery', 'Other')),
                                
                                #date range
                                dateRangeInput("Date_Range", "Choose a date range", 
                                               start = "2015-10-01", end = "2015-12-31", 
                                               min = "2000-01-01", max = "2015-12-31"),
                                
                                #start and end hour
                                sliderInput("IntHour", "Start time", 0, 23, 0, step = 1),
                                sliderInput("EndHour", "End time", 0, 23, 23, step = 1),
                                
                                h4("Click the Update button to see the map: "),
                                #update button
                                actionButton("button", "Update", 
                                             style="color: #fff; background-color: #337ab7; border-color: #2e6da4")
                              ),
                              
                              mainPanel(
                                leafletOutput("map", width = "100%", height = 650)
                              )
                )
        ), 
        ################################################################################################    Complaints complaints part                
        tabItem(tabName = "complaint",
                # sidebarLayout(position = "right",
                fluidRow(
                  column(4, selectInput("Crime.Type", label = "Crime Type", 
                                        choices = c('Arson',
                                                    'Weapons', 'Fraud', 'GrandLarceny', 'Robbery', 'Burglary', 'Homicide', 'Drugs', 'Rape',
                                                    'GrandLarcenyAuto', 'CriminalMischief', 'FelonyAssault', 'Forgery', 'Other')))
                  
                ),
                box(width = 12,wordcloud2Output("wordcloud", width = "100%", height = "400px")),
                box(width = 12, plotlyOutput("ggplotly"))
        ),
        
        
        ################################################################################################ data set part
        tabItem(tabName = "rawdata",
                box(width = 12,
                    DT::dataTableOutput("table"),downloadButton('downloadData', 'Download')
                )
                
        )
      )
    )
  )
)
