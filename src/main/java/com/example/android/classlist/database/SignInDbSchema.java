package com.example.android.classlist.database;

/**
 * Created by User on 6/3/2017.
 * Created to define table and columns in database
 */

public class SignInDbSchema {
    /**
     * Describes the table
     */
    public static final class SignInTable{
        // Name of table in database
        public static final String NAME = "signing_in";

        /**
         * Describes the columns
         */
        public static final class Cols{
            public static final String REG_NO = "reg_no";
            public static final String NAME = "name";
        }
    }
}
