package com.example.android.classlist;

import android.text.TextWatcher;

/**
 * Created by User on 5/25/2017.
 * Interface for common methods that need to be overriden for different uses
 */

interface Extras {

    /**
     * Method that connects to next activity
     */
    void moveToScreen(String ...args);

    /**
     * Checks whether field is empty
     */
    abstract class MyTextWatcher implements TextWatcher {
        boolean empty = true;

        boolean nonEmpty() {
            return !empty;
        }
    }
}
