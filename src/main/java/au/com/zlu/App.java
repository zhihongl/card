package au.com.zlu;


import au.com.zlu.model.CreditCardTransaction;
import au.com.zlu.model.FraudTransaction;
import au.com.zlu.utils.FraudListUtils;

import java.io.IOException;
import java.time.format.DateTimeParseException;
import java.util.List;

/**
 * Implementation of application entry point
 */
public class App {
    /**
     * main entry point of the application
     * takes 2 args
     * -  transaction file path eg: /path/to/transaction_file
     * -  price threshold eg: XX
     *
     * @param args
     * @return Nothing
     */
    public static void main(String[] args) {
        if (args.length != 2) {
            System.err.println("Please provide transaction file path and price threshold");
            System.exit(1);
        }
        new App().StartFraudChecking(args[0], args[1]);
    }

    /**
     * prepare to start checking fraud transaction
     *
     * @param inputFilePath
     * @param inputPriceThreshold
     * @return Nothing
     */
    public void StartFraudChecking(String inputFilePath, String inputPriceThreshold) {
        double priceThreshold;
        // validate all the inputs parameters
        try {
            priceThreshold = Double.parseDouble(inputPriceThreshold);
        } catch (NumberFormatException e) {
            System.err.println("Price threshold format is incorrect.");
            return;
        }

        // read the list of transactions in chronological order
        FraudDetection fraudDetection = new FraudDetection();
        List<CreditCardTransaction> transactionList = null;
        try {
            transactionList = fraudDetection.readTransactionListFromFile(inputFilePath);
        } catch (DateTimeParseException e) {
            System.err.println("Date format is incorrect.");
            System.exit(1);
        } catch (NumberFormatException e) {
            System.err.println("Amount format is incorrect.");
            System.exit(1);
        } catch (IOException e) {
            System.err.println("File path is invalid.");
            System.exit(1);
        } catch (ArrayIndexOutOfBoundsException e) {
            System.err.println("Data is invalid.");
            System.exit(1);
        }
        // start checking fraud transaction
        List<FraudTransaction> fraudList = fraudDetection.detectFraud(transactionList, priceThreshold);

        // print out fraud transaction list
        FraudListUtils.printFraudList(fraudList);
    }

}
