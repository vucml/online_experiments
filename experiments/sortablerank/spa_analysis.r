# Load necessary libraries
library(dplyr)
library(ggplot2)
library(tidyr)

# List of datasets
dataset_paths <- list(
  first_pass = "/Users/jordangunn/jatos/study_assets_root/online_experiments/experiments/sortablerank/first_pass_data.csv",
  second_pass = "/Users/jordangunn/jatos/study_assets_root/online_experiments/experiments/sortablerank/second_pass_data.csv"
)

# Function to process data and generate plots
process_and_plot <- function(data, dataset_name, plot_suffix, group_vars) {
  # If the data is empty, skip processing
  if (nrow(data) == 0) {
    message("No data to process for ", plot_suffix)
    return(NULL)
  }
  
  # Step 1: Calculate counts of each shared feature level for each subject
  feature_counts <- data %>%
    group_by(subject) %>%
    summarize(
      condition = first(condition),
      count_0 = sum(shared_features == 0),
      count_1 = sum(shared_features == 1),
      count_2 = sum(shared_features == 2),
      count_3 = sum(shared_features == 3),
      .groups = 'drop'
    )
  
  # Step 2: Join counts back to the main data frame
  data <- data %>%
    select(-condition) %>%
    left_join(feature_counts, by = "subject")
  
  # Step 3: Calculate expected proportions for each subject and shared feature level
  expected_proportions <- data %>%
    group_by(subject) %>%
    summarize(
      condition = first(condition),
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
    pivot_wider(
      names_from = shared_features,
      values_from = observed_count,
      names_prefix = "observed_",
      values_fill = list(observed_count = 0)
    ) %>%
    mutate(
      observed_prop_0 = ifelse("observed_0" %in% names(.), observed_0 / 4, 0),
      observed_prop_1 = ifelse("observed_1" %in% names(.), observed_1 / 4, 0),
      observed_prop_2 = ifelse("observed_2" %in% names(.), observed_2 / 4, 0),
      observed_prop_3 = ifelse("observed_3" %in% names(.), observed_3 / 4, 0)
    ) %>%
    select(subject, observed_prop_0, observed_prop_1, observed_prop_2, observed_prop_3)
  
  # Step 5: Join expected and observed proportions
  data_proportions <- expected_proportions %>%
    left_join(observed_proportions, by = "subject")
  
  # Step 6: Calculate proportional ratios
  data_proportions <- data_proportions %>%
    mutate(
      ratio_0 = observed_prop_0 / expected_prop_0,
      ratio_1 = observed_prop_1 / expected_prop_1,
      ratio_2 = observed_prop_2 / expected_prop_2,
      ratio_3 = observed_prop_3 / expected_prop_3
    )
  
  # Step 7: Reshape data to long format
  data_long <- data_proportions %>%
    pivot_longer(
      cols = starts_with("ratio_"),
      names_to = "shared_feature_level",
      values_to = "selection_ratio"
    ) %>%
    mutate(
      shared_feature_level = as.numeric(gsub("ratio_", "", shared_feature_level))
    )
  
  # Step 8: Add grouping variables to data_long
  grouping_info <- data %>%
    select(subject, all_of(group_vars), condition) %>%
    distinct()
  
  data_long <- data_long %>%
    left_join(grouping_info, by = "subject")
  
  # Step 9: Calculate average selection ratio by shared feature level and grouping variables
  average_ratios <- data_long %>%
    group_by(across(all_of(c("condition", group_vars))), shared_feature_level) %>%
    summarize(mean_ratio = mean(selection_ratio, na.rm = TRUE), .groups = 'drop')
  
  # Check if average_ratios is empty
  if (nrow(average_ratios) == 0) {
    message("No data to plot for ", plot_suffix)
    return(NULL)
  }
  
  # Step 10: Plot
  p <- ggplot(average_ratios, aes(x = shared_feature_level, y = mean_ratio,
                                  color = interaction(!!!syms(c("condition", group_vars))),
                                  group = interaction(!!!syms(c("condition", group_vars))))) +
    geom_line() +
    geom_point() +
    labs(
      x = "Number of Shared Features",
      y = "Average Selection Ratio",
      title = paste("Homophily Check:", dataset_name, plot_suffix)
    )
  
  # Save the plot
  plot_filename <- paste0("homophily_check_", dataset_name, plot_suffix, ".png")
  ggsave(plot_filename, plot = p)
}

# Loop through each dataset and generate plots
for (dataset_name in names(dataset_paths)) {
  # Load the data
  data <- read.csv(dataset_paths[[dataset_name]])
  
  # Define grouping combinations based on dataset
  if (dataset_name == "first_pass") {
    grouping_combinations <- list(
      list(name = "_overall", vars = character(0)),
      list(name = "_task_type", vars = c("task_type"))
      # Ordering has only one level in first_pass_data
    )
  } else {
    grouping_combinations <- list(
      list(name = "_overall", vars = character(0)),
      list(name = "_ordering", vars = c("ordering")),
      list(name = "_task_type", vars = c("task_type")),
      list(name = "_task_type_ordering", vars = c("task_type", "ordering"))
    )
  }
  
  # Generate plots for each grouping combination
  for (grouping in grouping_combinations) {
    group_name <- grouping$name
    group_vars <- grouping$vars
    
    if (length(group_vars) == 0) {
      # Overall plot
      process_and_plot(data, dataset_name, group_name, group_vars)
    } else {
      # Get unique combinations of grouping variables
      combinations <- unique(data[group_vars])
      for (i in 1:nrow(combinations)) {
        subset_data <- data
        plot_suffix <- group_name
        current_combination <- combinations[i, , drop = FALSE]
        for (var in group_vars) {
          value <- current_combination[[var]]
          subset_data <- subset_data[subset_data[[var]] == value, ]
          plot_suffix <- paste0(plot_suffix, "_", var, "_", value)
        }
        # Check if subset_data is empty
        if (nrow(subset_data) == 0) {
          message("No data for ", plot_suffix, "; skipping.")
          next
        }
        # Process and plot the subset
        process_and_plot(subset_data, dataset_name, plot_suffix, group_vars)
      }
    }
  }
}