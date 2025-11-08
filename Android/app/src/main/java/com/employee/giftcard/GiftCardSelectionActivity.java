package com.employee.giftcard;

import androidx.appcompat.app.AppCompatActivity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.LinearLayout;

public class GiftCardSelectionActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_giftcard_selection);

        // Setup click listeners for each gift card type
        setupGiftCardButton(R.id.btnPaypal, "PayPal");
        setupGiftCardButton(R.id.btnAmazon, "Amazon");
        setupGiftCardButton(R.id.btnApple, "Apple / iTunes");
        setupGiftCardButton(R.id.btnGooglePlay, "Google Play");
        setupGiftCardButton(R.id.btnRazer, "Razer Gold");
        setupGiftCardButton(R.id.btnSteam, "Steam");
        setupGiftCardButton(R.id.btnVisa, "Visa Prepaid");
        setupGiftCardButton(R.id.btnNetflix, "Netflix");
        setupGiftCardButton(R.id.btnSpotify, "Spotify Premium");
        setupGiftCardButton(R.id.btnXbox, "Xbox / Microsoft");
        setupGiftCardButton(R.id.btnPlaystation, "PlayStation Network");
    }

    private void setupGiftCardButton(int viewId, final String cardType) {
        LinearLayout button = findViewById(viewId);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                selectGiftCard(cardType);
            }
        });
    }

    private void selectGiftCard(String cardType) {
        // Pass the selected card type back to MainActivity
        Intent intent = new Intent(this, MainActivity.class);
        intent.putExtra("SELECTED_GIFTCARD", cardType);
        intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        startActivity(intent);
        finish();
    }
}
