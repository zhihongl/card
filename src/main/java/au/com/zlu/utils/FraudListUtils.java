package au.com.zlu.utils;

import au.com.zlu.model.FraudTransaction;

import java.util.List;

/**
 * All the reuseable functions for fraud list
 */
public class FraudListUtils {

    /**
     * print out the fraud transaction
     *
     * @param fraudList
     * @return Nothing
     */
    public static void printFraudList(List<FraudTransaction> fraudList) {
        if (fraudList.isEmpty()) {
            System.out.println("No fraud transaction found.");
        }
        for (FraudTransaction fraud : fraudList) {
            System.out.println(fraud.getHashCardNumber());
        }

    }

}
