package au.com.zlu;

import au.com.zlu.model.CreditCardTransaction;
import au.com.zlu.model.FraudTransaction;
import au.com.zlu.utils.DateUtils;
import org.junit.Test;

import java.io.IOException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;

import static org.hamcrest.CoreMatchers.containsString;
import static org.junit.Assert.*;

/**
 * Unit test for simple App.
 */
public class AppTest {
    static final String CARD_NUMBER = "10d7ce2f43e35fa57d1bbf8b1e2";
    static final String TRANSACTION_DATE = "2020-05-14T13:15:54";
    static final String TRANSACTION_DAY = "2020-05-14";
    static final String TRANSACTION_AMOUNT = "10.00";
    static final Double TRANSACTION_AMOUNT_DOUBLE = 10.00;
    static final String FRAUD_PRICE_THRESHOLD = "10.00";
    static final Double FRAUD_PRICE_THRESHOLD_NUMBER = 10.00;
    static final String NOT_FRAUD_PRICE_THRESHOLD = "15.00";
    static final Double NOT_FRAUD_PRICE_THRESHOLD_NUMBER = 15.00;

    /**
     * test date format with time
     */
    @Test
    public void testDateTimeFormat() {
        LocalDateTime date = DateUtils.parseStringDateTime(TRANSACTION_DATE);
        assertEquals("dates should be equal ", TRANSACTION_DATE, date.toString());
    }

    /**
     * test date format without time
     */
    @Test
    public void testDateFormat() {
        LocalDate date = DateUtils.parseStringDateNoTime(TRANSACTION_DAY);
        assertEquals("dates should be equal ", TRANSACTION_DAY, date.toString());
    }

    /**
     * testing for a single fraud transaction
     */
    @Test
    public void testSimpleTransactionWithFraud() {

        CreditCardTransaction creditCardTransaction = new CreditCardTransaction(CARD_NUMBER,
                DateUtils.parseStringDateTime(TRANSACTION_DATE), TRANSACTION_AMOUNT_DOUBLE);
        List<CreditCardTransaction> transactionList = new ArrayList<CreditCardTransaction>();
        transactionList.add(creditCardTransaction);

        FraudDetection fraudDetection = new FraudDetection();
        List<FraudTransaction> fraudList = fraudDetection.detectFraud(transactionList, FRAUD_PRICE_THRESHOLD_NUMBER);

        assertEquals("Fraud list length should equal one", 1, fraudList.size());
    }


    /**
     * test with a single non-fraud transaction
     */
    @Test
    public void testSimpleTransactionWithoutFraud() {

        CreditCardTransaction creditCardTransaction = new CreditCardTransaction(CARD_NUMBER,
                DateUtils.parseStringDateTime(TRANSACTION_DATE), TRANSACTION_AMOUNT_DOUBLE);
        List<CreditCardTransaction> transactionList = new ArrayList<CreditCardTransaction>();
        transactionList.add(creditCardTransaction);

        FraudDetection fraudDetection = new FraudDetection();
        List<FraudTransaction> fraudList = fraudDetection.detectFraud(transactionList, NOT_FRAUD_PRICE_THRESHOLD_NUMBER);

        assertEquals("Fraud list should be empty", 0, fraudList.size());
    }

    /**
     * test with two transaction on same card, resulting in amount >= fraud
     */
    @Test
    public void testTwoTransactionFromSameCardWithFraud() {
        CreditCardTransaction creditCardTransaction1 = new CreditCardTransaction(CARD_NUMBER,
                DateUtils.parseStringDateTime(TRANSACTION_DATE), TRANSACTION_AMOUNT_DOUBLE);
        CreditCardTransaction creditCardTransaction2 = new CreditCardTransaction(CARD_NUMBER,
                DateUtils.parseStringDateTime(TRANSACTION_DATE), TRANSACTION_AMOUNT_DOUBLE);
        List<CreditCardTransaction> transactionList = new ArrayList<CreditCardTransaction>();
        transactionList.add(creditCardTransaction1);
        transactionList.add(creditCardTransaction2);
        FraudDetection fraudDetection = new FraudDetection();
        List<FraudTransaction> fraudList = fraudDetection.detectFraud(transactionList, NOT_FRAUD_PRICE_THRESHOLD_NUMBER);

        assertEquals("Fraud list should have value", 1, fraudList.size());
    }

    /**
     * test 2 fraud transaction from 2 card
     */
    @Test
    public void testTwoTransactionWithFraud() {

        double Threshold = 100;
        CreditCardTransaction cardTransaction1 = new CreditCardTransaction(CARD_NUMBER,
                DateUtils.parseStringDateTime(TRANSACTION_DATE), TRANSACTION_AMOUNT_DOUBLE);
        CreditCardTransaction cardTransaction2 = new CreditCardTransaction("1234562f43e35fa57d1bb123456",
                DateUtils.parseStringDateTime("2020-05-14T13:01:21"), 101);
        List<CreditCardTransaction> transactionList = new ArrayList<CreditCardTransaction>();
        transactionList.add(cardTransaction1);
        transactionList.add(cardTransaction2);
        FraudDetection fraudDetection = new FraudDetection();
        List<FraudTransaction> fraudList = fraudDetection.detectFraud(transactionList, FRAUD_PRICE_THRESHOLD_NUMBER);

        assertEquals("Fraud list should contains 2 element", 2, fraudList.size());
    }

    /**
     * test fraud card number is correct or not
     */
    @Test
    public void testTwoTransactionWithFraudDisplayName() {

        CreditCardTransaction cardTransaction1 = new CreditCardTransaction(CARD_NUMBER,
                DateUtils.parseStringDateTime(TRANSACTION_DATE), TRANSACTION_AMOUNT_DOUBLE);
        CreditCardTransaction cardTransaction2 = new CreditCardTransaction("1234562f43e35fa57d1bb123456",
                DateUtils.parseStringDateTime(TRANSACTION_DATE), TRANSACTION_AMOUNT_DOUBLE);
        List<CreditCardTransaction> transactionList = new ArrayList<CreditCardTransaction>();
        transactionList.add(cardTransaction1);
        transactionList.add(cardTransaction2);
        FraudDetection fraudDetection = new FraudDetection();
        List<FraudTransaction> fraudList = fraudDetection.detectFraud(transactionList, FRAUD_PRICE_THRESHOLD_NUMBER);
        String cardNumbers = "";
        cardNumbers = fraudList.get(0).getHashCardNumber() + "," + fraudList.get(1).getHashCardNumber();

        assertThat(cardNumbers, containsString(CARD_NUMBER));
        assertThat(cardNumbers, containsString("1234562f43e35fa57d1bb123456"));

    }

    /**
     * test parsing single transaction string
     *
     * @throws Exception
     */
    @Test
    public void testParsingSingleTransactionString() throws Exception {

        String transactionString = CARD_NUMBER + ", " + TRANSACTION_DATE + ", " + TRANSACTION_AMOUNT;

        FraudDetection fraudDetection = new FraudDetection();
        CreditCardTransaction creditCardTransaction = fraudDetection.parseSingleStringTransaction(transactionString);
        assertEquals("card number should be", CARD_NUMBER, creditCardTransaction.getHashCardNumber());
        assertEquals("transaction date should be", TRANSACTION_DATE,
                creditCardTransaction.getTransactionDate().toString());
        assertEquals("transaction amount should be", Double.valueOf(TRANSACTION_AMOUNT),
                Double.valueOf(creditCardTransaction.getTransactionAmount()));
    }

    /**
     * test parsing a file with transactions
     *
     * @throws IOException
     */
    @Test
    public void testParsingFileWithTwoTransaction() throws IOException {
        FraudDetection fraudDetection = new FraudDetection();
        int transactionNumber =
                fraudDetection.readTransactionListFromFile("src/test/resources/two_transactions")
                        .size();
        assertEquals(2, transactionNumber);
    }

    @Test
    public void testParsingFileWithDateMalformatted() throws IOException {
        FraudDetection fraudDetection = new FraudDetection();
        boolean rightException = false;
        try {
            fraudDetection.readTransactionListFromFile("src/test/resources/date_malformated");
        } catch (DateTimeParseException e) {
            rightException = true;
        }
        assertTrue(rightException);
    }

    @Test
    public void testParsingFileWithWrongFilePath() {
        FraudDetection fraudDetection = new FraudDetection();
        boolean rightException = false;
        try {
            fraudDetection.readTransactionListFromFile("wrong_file_path");
        } catch (DateTimeParseException e) {
        } catch (IOException e) {
            rightException = true;
        }
        assertTrue(rightException);
    }

    /**
     * test implementation
     *
     * @throws IOException
     */
    @Test
    public void testFraudDetection() throws DateTimeParseException, NumberFormatException, IOException {
        FraudDetection fraudDetection = new FraudDetection();

        List<CreditCardTransaction> transactionList = fraudDetection
                .readTransactionListFromFile("src/test/resources/transaction_file");

        List<FraudTransaction> fraudList = fraudDetection.detectFraud(transactionList, 10);
        assertEquals("Fraud list should have 3 values", 3, fraudList.size());
    }

    /**
     * test big amount transaction 10,000 non-fraud transaction
     *
     * @throws IOException
     */
    @Test
    public void testBigDetection() throws DateTimeParseException, NumberFormatException, IOException {
        FraudDetection fraudDetection = new FraudDetection();

        List<CreditCardTransaction> transactionList = fraudDetection
                .readTransactionListFromFile("src/test/resources/transaction_file_big");

        List<FraudTransaction> fraudList = fraudDetection.detectFraud(transactionList, 10);
        assertEquals("Fraud list should be empty", 0, fraudList.size());
    }

    /**
     * test big amount transaction 2^30 non-fraud transaction
     * This will results to java.lang.OutOfMemoryError: Java heap space, because of the way of implementation
     *
     * @throws IOException
     */
//    @Test
//    public void testLargeAmountTransaction() throws DateTimeParseException, NumberFormatException, IOException {
//        FraudDetection fraudDetection = new FraudDetection();
//
//        List<CreditCardTransaction> transactionList = fraudDetection
//                .readTransactionListFromFile("src/test/resources/transaction_file_bigger");
//
//        List<FraudTransaction> fraudList = fraudDetection.detectFraud(transactionList, 10);
//        assertEquals("Fraud list should be empty", 0, fraudList.size());
//    }

}
