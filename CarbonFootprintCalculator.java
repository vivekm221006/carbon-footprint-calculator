import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class CarbonFootprintCalculator extends JFrame {

    private JTextField transportField, electricityField;
    private JComboBox<String> foodChoice;
    private JLabel resultLabel;

    public CarbonFootprintCalculator() {
        setTitle("Carbon Footprint Calculator");
        setSize(400, 300);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new GridLayout(5, 2));

        // UI Components
        add(new JLabel("Transport (km per day):"));
        transportField = new JTextField();
        add(transportField);

        add(new JLabel("Electricity Usage (kWh per day):"));
        electricityField = new JTextField();
        add(electricityField);

        add(new JLabel("Food Choice:"));
        foodChoice = new JComboBox<>(new String[]{"Meat-based (2.5 kg)", "Vegetarian (1.5 kg)", "Vegan (1.0 kg)"});
        add(foodChoice);

        JButton calculateButton = new JButton("Calculate");
        add(calculateButton);

        resultLabel = new JLabel("Your CO₂ emissions: 0 kg");
        add(resultLabel);

        // Button Action
        calculateButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                calculateFootprint();
            }
        });

        setVisible(true);
    }

    private void calculateFootprint() {
        try {
            double transport = Double.parseDouble(transportField.getText()) * 0.12; // 0.12 kg CO2 per km
            double electricity = Double.parseDouble(electricityField.getText()) * 0.92; // 0.92 kg CO2 per kWh
            double food = foodChoice.getSelectedIndex() == 0 ? 2.5 : foodChoice.getSelectedIndex() == 1 ? 1.5 : 1.0;

            double totalEmissions = transport + electricity + food;
            resultLabel.setText("Your CO₂ emissions: " + String.format("%.2f", totalEmissions) + " kg");
        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Please enter valid numbers!", "Input Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    public static void main(String[] args) {
        new CarbonFootprintCalculator();
    }
}

