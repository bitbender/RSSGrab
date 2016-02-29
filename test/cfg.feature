Feature: The configuration holder

  Scenario: access configuration parameters
    Given we created a config object from a file
    When we access the parameters
    Then the parameters defined in the file should be accessible