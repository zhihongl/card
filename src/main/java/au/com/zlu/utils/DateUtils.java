package au.com.zlu.utils;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * All the date related reuse functions
 */
public class DateUtils {

    /**
     * Date format used in this application
     */
    public final static DateTimeFormatter CARD_TRANSACTION_DATE_TIME_FORMAT = DateTimeFormatter.ISO_LOCAL_DATE_TIME;

    public final static DateTimeFormatter CARD_TRANSACTION_DATE_FORMAT = DateTimeFormatter.ISO_LOCAL_DATE;

    public static String parseLocalDateTimeToStringNoTime(LocalDateTime localDateTime) {
        final String dateString = localDateTime.format(CARD_TRANSACTION_DATE_FORMAT);
		return dateString;
    }

    public static LocalDate parseStringDateNoTime(String dateString) {
        final LocalDate date = LocalDate.parse(dateString, CARD_TRANSACTION_DATE_FORMAT);
        return date;
    }

    public static LocalDateTime parseStringDateTime(String dateString) {
        final LocalDateTime date = LocalDateTime.parse(dateString, CARD_TRANSACTION_DATE_TIME_FORMAT);
        return date;
    }

}
