package au.com.zlu.model;

import java.time.LocalDate;

/**
 * Implementation of Fraud detection
 */
public class TransactionDateAndAmount {

    private double totalTransactionAmount;

    private LocalDate fraudDate;

    public TransactionDateAndAmount(LocalDate fraudDate, double totalTransactionAmount) {
        this.totalTransactionAmount = totalTransactionAmount;
        this.fraudDate = fraudDate;
    }

    public double getTotalTransactionAmount() {
        return totalTransactionAmount;
    }

    public void setTotalTransactionAmount(double totalTransactionAmount) {
        this.totalTransactionAmount = totalTransactionAmount;
    }

    public LocalDate getFraudDate() {
        return fraudDate;
    }

    public void setFraudDate(LocalDate fraudDate) {
        this.fraudDate = fraudDate;
    }
}
