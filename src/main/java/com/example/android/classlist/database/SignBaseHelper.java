package com.example.android.classlist.database;

import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import com.example.android.classlist.database.SignInDbSchema.SignInTable;

/**
 * Created by User on 6/3/2017.
 * 1. Checks whether database exists.
 * 2. Create it and put initial data if it doesn't
 * 3. Open and check version of SignInDbSchema if exists
 * 4. Upgrade to new version if old
 */

public class SignBaseHelper extends SQLiteOpenHelper {
    private static final int VERSION = 1;
    private static final String DATABASE_NAME = "signInDb.db";

    public SignBaseHelper(Context context){
        super(context, DATABASE_NAME, null, VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase sqLiteDatabase) {
        sqLiteDatabase.execSQL("create table " + SignInTable.NAME + "(" +
                " _id integer primary key autoincrement, " +
                SignInTable.Cols.REG_NO + " unique, " +
                SignInTable.Cols.NAME  +
                ")"
        );
    }

    @Override
    public void onUpgrade(SQLiteDatabase sqLiteDatabase, int i, int i1) {

    }
}
