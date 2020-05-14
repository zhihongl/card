package au.com.zlu;

import au.com.zlu.model.CreditCardTransaction;
import au.com.zlu.model.FraudTransaction;
import au.com.zlu.utils.DateUtils;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeParseException;
import java.util.*;
import java.util.stream.Stream;

/**
 * Implementation of Fraud detection
 */
public class FraudDetection {

    protected Map<String, HashMap<String, Double>> cardMap = new HashMap<String, HashMap<String, Double>>();

    protected List<FraudTransaction> fraudList = new ArrayList<FraudTransaction>();

    protected double amountThreshold;

    /**
     * start fraud detection
     *
     * @param transactionList
     * @param amountThreshold
     * @return FraudTransaction
     */
    public List<FraudTransaction> detectFraud(List<CreditCardTransaction> transactionList, double amountThreshold) {

        // process transactions
        this.amountThreshold = amountThreshold;
        for (CreditCardTransaction creditCardTransaction : transactionList) {

            // process transaction details
            String transactionDateString =
                    DateUtils.parseLocalDateTimeToStringNoTime(creditCardTransaction.getTransactionDate());
            String cardNumber = creditCardTransaction.getHashCardNumber();
            double transactionAmount = creditCardTransaction.getTransactionAmount();

            // add transaction detail (transaction date and amount) into card hashmap
            addCardAndAmount(cardNumber, transactionDateString, transactionAmount);
        }

        // checking if any transaction is fraud
        generateFraudList();

        return fraudList;
    }

    /**
     * generate fraud list
     */
    private void generateFraudList() {
        cardMap.forEach((cardNumber, transactionDateAndAmountMap) -> {
            Optional<Map.Entry<String, Double>> result =
                    transactionDateAndAmountMap.entrySet().stream()
                            .filter(obj -> obj.getValue() >= amountThreshold).findFirst();
            if (result.isPresent()) {
                fraudList.add(new FraudTransaction(cardNumber));
            }
        });
    }

    /**
     * add transaction detials into card map
     *
     * @param cardNumber
     * @param transactionDateString Transaction date in string format
     * @param transactionAmount
     * @return Nothing
     */
    private void addCardAndAmount(String cardNumber, String transactionDateString, double transactionAmount) {

        if (cardMap.containsKey(cardNumber)) {
            // if the card number in card map then update transaction details
            HashMap<String, Double> transactionDateAndAmountMap = cardMap.get(cardNumber);
            if (transactionDateAndAmountMap.containsKey(transactionDateString)) {
                double oldTotalAmount = transactionDateAndAmountMap.get(transactionDateString);
                double newTotalAmount = transactionAmount + oldTotalAmount;
                transactionDateAndAmountMap.put(transactionDateString, newTotalAmount);
            } else {
                transactionDateAndAmountMap.put(transactionDateString, transactionAmount);
            }
            cardMap.put(cardNumber, transactionDateAndAmountMap);
        } else {
            // if not then create an empty transaction details
            HashMap<String, Double> newTransactionDateAndAmountMap = new HashMap<String, Double>();
            newTransactionDateAndAmountMap.put(transactionDateString, transactionAmount);
            cardMap.put(cardNumber, newTransactionDateAndAmountMap);
        }

    }

    /**
     * process file data into credit card transaction list
     *
     * @param inputPath
     * @return List<CreditCardTransaction>
     * @throws IOException
     * @throws DateTimeParseException
     * @throws NumberFormatException
     */
    public List<CreditCardTransaction> readTransactionListFromFile(String inputPath)
            throws IOException, DateTimeParseException, NumberFormatException {

        List<CreditCardTransaction> transactionList = new ArrayList<CreditCardTransaction>();

        Stream<String> lines = Files.lines(Paths.get(inputPath));
        lines.forEach(line -> {
            CreditCardTransaction transaction = parseSingleStringTransaction(line);
            transactionList.add(transaction);
        });
        lines.close();
        return transactionList;
    }

    /**
     * parse a string to a credit card transaction
     *
     * @param line
     * @return CreditCardTransaction
     */
    public CreditCardTransaction parseSingleStringTransaction(String line) {
        String[] groups = line.replaceAll("\\s+", "").split(",");
        String cardNumber = groups[0];
        LocalDateTime transactionDate = DateUtils.parseStringDateTime(groups[1]);
        double amount = Double.parseDouble(groups[2]);

        return new CreditCardTransaction(cardNumber, transactionDate, amount);
    }

}
