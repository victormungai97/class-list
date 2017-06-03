package com.example.android.classlist.database;

import android.database.Cursor;
import android.database.CursorWrapper;

import com.example.android.classlist.database.SignInDbSchema.SignInTable;

/**
 * Created by User on 6/3/2017.
 * Class that wraps a cursor
 */

public class SignInCursorWrapper extends CursorWrapper{

    public SignInCursorWrapper(Cursor cursor) {
        super(cursor);
    }

    public String getRegNo() {
        return getString(getColumnIndex(SignInTable.Cols.REG_NO));
    }
}
