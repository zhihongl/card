package au.com.zlu.model;

public class FraudTransaction {

    private String hashedCardNumber;

    public FraudTransaction(String hashedCardNumber) {
        this.hashedCardNumber = hashedCardNumber;
    }

    public String getHashCardNumber() {
        return hashedCardNumber;
    }

    public void setHashedCardNumber(String hashedCardNumber) {
        this.hashedCardNumber = hashedCardNumber;
    }

}
