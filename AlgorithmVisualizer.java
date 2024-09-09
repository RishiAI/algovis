import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class AlgorithmVisualizer extends JFrame {
    private JPanel controlPanel;
    private VisualizationPanel visualizationPanel;
    private List<Integer> data;
    private final int DATA_SIZE = 50;
    private final int MAX_VALUE = 100;

    public AlgorithmVisualizer() {
        setTitle("Algorithm Visualizer");
        setSize(800, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());

        initializeData();
        initializeUI();
    }

    private void initializeData() {
        data = new ArrayList<>();
        Random random = new Random();
        for (int i = 0; i < DATA_SIZE; i++) {
            data.add(random.nextInt(MAX_VALUE) + 1);
        }
    }

    private void initializeUI() {
        controlPanel = new JPanel();
        visualizationPanel = new VisualizationPanel();

        JButton bubbleSortButton = new JButton("Bubble Sort");
        bubbleSortButton.addActionListener(e -> bubbleSort());

        JButton resetButton = new JButton("Reset");
        resetButton.addActionListener(e -> resetData());

        controlPanel.add(bubbleSortButton);
        controlPanel.add(resetButton);

        add(controlPanel, BorderLayout.NORTH);
        add(visualizationPanel, BorderLayout.CENTER);
    }

    private void bubbleSort() {
        new Thread(() -> {
            for (int i = 0; i < data.size() - 1; i++) {
                for (int j = 0; j < data.size() - i - 1; j++) {
                    if (data.get(j) > data.get(j + 1)) {
                        int temp = data.get(j);
                        data.set(j, data.get(j + 1));
                        data.set(j + 1, temp);
                        visualizationPanel.repaint();
                        try {
                            Thread.sleep(50);
                        } catch (InterruptedException e) {
                            e.printStackTrace();
                        }
                    }
                }
            }
        }).start();
    }

    private void resetData() {
        initializeData();
        visualizationPanel.repaint();
    }

    private class VisualizationPanel extends JPanel {
        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            int width = getWidth();
            int height = getHeight();
            int barWidth = width / DATA_SIZE;

            for (int i = 0; i < data.size(); i++) {
                int barHeight = (int) ((double) data.get(i) / MAX_VALUE * height);
                g.setColor(Color.BLUE);
                g.fillRect(i * barWidth, height - barHeight, barWidth - 1, barHeight);
            }
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            AlgorithmVisualizer visualizer = new AlgorithmVisualizer();
            visualizer.setVisible(true);
        });
    }
}