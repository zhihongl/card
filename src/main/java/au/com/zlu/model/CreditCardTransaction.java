package au.com.zlu.model;

import java.time.LocalDateTime;

/**
 * a single credit card transaction
 */
public class CreditCardTransaction {

    private String hashCardNumber;

    private LocalDateTime transactionDate;

    private double transactionAmount;


    public CreditCardTransaction(String hashCardNumber, LocalDateTime transactionDate, double transactionAmount) {
        this.hashCardNumber = hashCardNumber;
        this.transactionDate = transactionDate;
        this.transactionAmount = transactionAmount;

    }

    public String getHashCardNumber() {
        return hashCardNumber;
    }

    public void setHashCardNumber(String hashCardNumber) {
        this.hashCardNumber = hashCardNumber;
    }

    public double getTransactionAmount() {
        return transactionAmount;
    }

    public void setTransactionAmount(double transactionAmount) {
        this.transactionAmount = transactionAmount;
    }

    public LocalDateTime getTransactionDate() {
        return transactionDate;
    }

    public void setTransactionDate(LocalDateTime transactionDate) {
        this.transactionDate = transactionDate;
    }

}
