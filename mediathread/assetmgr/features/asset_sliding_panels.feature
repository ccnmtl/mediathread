Feature: Sliding Panels in the Asset View
    
    Scenario Outline: 1. Full Collection at various resolutions
        Using selenium
        Given there are sample assets
        Given I am instructor_one in Sample Course
        Given my browser resolution is <width> x <height>
    
        # Full Collection
        When I click the "View Full Collection" link
        Given the asset workspace is loaded

        # View an individual asset
        When I click the "MAAP Award Reception" link
        Then there is a minimized Collection panel
        And there is an open Asset panel
        
        # Verify the asset is really there
        The item header is "MAAP Award Reception"
        
        Finished using Selenium
        
      Examples:
        | width | height |
        | 900   | 500    |
        | 1024  | 768    |
        | 1280  | 800    |
        | 1440  | 900    |
        
    Scenario Outline: 2. Individual Item View
        Using selenium
        Given there are sample assets
        Given I am instructor_one in Sample Course
        Given my browser resolution is <width> x <height>
    
        # View an individual asset
        When I access the url "/asset/1/"
        Given the asset workspace is loaded
        Then there is a minimized Collection panel
        And there is an open Asset panel

        # Verify the asset is really there
        The item header is "MAAP Award Reception"
        
        Finished using Selenium
        
      Examples:
        | width | height |
        | 900   | 500    |
        | 1024  | 768    |
        | 1280  | 800    |
        | 1440  | 900    |