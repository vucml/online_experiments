# Load necessary libraries
library(dplyr)
library(ggplot2)
library(tidyr)

# Load the data
data <- read.csv("/Users/jordangunn/jatos/study_assets_root/online_experiments/experiments/sortablerank/second_pass_data.csv")

# Step 1: Calculate the counts of each shared feature level for each subject and retain condition
feature_counts <- data %>%
  group_by(subject) %>%
  summarize(
    condition = first(condition),  # Ensure condition is retained for each subject
    count_0 = sum(shared_features == 0),
    count_1 = sum(shared_features == 1),
    count_2 = sum(shared_features == 2),
    count_3 = sum(shared_features == 3),
    .groups = 'drop'
  )

# Step 2: Join these counts back to the main data frame based on the subject
# Keep only one version of 'condition' in the resulting data
data <- data %>%
  select(-condition) %>%  # Remove condition from original data to avoid suffixes
  left_join(feature_counts, by = "subject")

# Step 3: Calculate expected proportions for each subject and shared feature level
expected_proportions <- data %>%
  group_by(subject) %>%
  summarize(
    condition = first(condition),  # Use condition from feature_counts
    expected_prop_0 = sum(shared_features == 0) / 9,
    expected_prop_1 = sum(shared_features == 1) / 9,
    expected_prop_2 = sum(shared_features == 2) / 9,
    expected_prop_3 = sum(shared_features == 3) / 9,
    .groups = 'drop'
  )

# Step 4: Calculate observed proportions for each subject and shared feature level
observed_proportions <- data %>%
  filter(chosen == 1) %>%
  group_by(subject, shared_features) %>%
  summarize(observed_count = n(), .groups = 'drop') %>%
  pivot_wider(names_from = shared_features, values_from = observed_count, 
              names_prefix = "observed_", values_fill = list(observed_count = 0)) %>%
  mutate(
    observed_prop_0 = observed_0 / 4,
    observed_prop_1 = observed_1 / 4,
    observed_prop_2 = observed_2 / 4,
    observed_prop_3 = observed_3 / 4
  ) %>%
  select(subject, observed_prop_0, observed_prop_1, observed_prop_2, observed_prop_3)

# Step 5: Join expected and observed proportions, retaining condition without duplicates
data_proportions <- expected_proportions %>%
  left_join(observed_proportions, by = "subject")

# Step 6: Calculate proportional ratios for each shared feature level
data_proportions <- data_proportions %>%
  mutate(
    ratio_0 = observed_prop_0 / expected_prop_0,
    ratio_1 = observed_prop_1 / expected_prop_1,
    ratio_2 = observed_prop_2 / expected_prop_2,
    ratio_3 = observed_prop_3 / expected_prop_3
  )

# Step 7: Reshape data to long format for easier plotting and comparison, ensuring condition stays consistent
data_long <- data_proportions %>%
  pivot_longer(cols = starts_with("ratio_"), 
               names_to = "shared_feature_level", 
               values_to = "selection_ratio") %>%
  mutate(
    shared_feature_level = as.numeric(gsub("ratio_", "", shared_feature_level))
  )

# Step 8: Calculate average selection ratio by shared feature level and condition
average_ratios <- data_long %>%
  group_by(condition, shared_feature_level) %>%
  summarize(mean_ratio = mean(selection_ratio, na.rm = TRUE), .groups = 'drop')

# Step 9: Plot average selection ratio against number of shared features for each condition
ggplot(average_ratios, aes(x = shared_feature_level, y = mean_ratio, color = condition, group = condition)) +
  geom_line() +
  geom_point() +
  labs(x = "Number of Shared Features", y = "Average Selection Ratio", 
       title = "Homophily Check: Average Selection Ratio by Shared Features and Condition")
  # theme_minimal()
ggsave("/Users/jordangunn/jatos/study_assets_root/online_experiments/experiments/sortablerank/figures/homophily_check.png")