# Credit Card Fraud Detector

This project is build in maven so just use normal maven command to build and test

### Prerequisites

Java

Maven

## Get started

This application takes two input values: 
1. transactions file path
2. price threshold

## What the application support

Currently this application only support limited amount of transaction like definate below 2^30 transaction. 
Because it will cause java.lang.OutOfMemoryError: Java heap space due to the way of implementation. 
And the last test case in AppTest file is regarding this. 

### Improvements

1. redesign the system to support 2^30 transactions, eg: involve Threads
2. use distributed system to handle this maybe try hadoop to handle big data
