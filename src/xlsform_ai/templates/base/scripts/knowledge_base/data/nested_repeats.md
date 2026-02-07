# Nested Repeats and Best Practices

Nested repeats are useful for hierarchical data (e.g., household -> plot -> crop).
They are harder to manage and should be used only when required.

## Example: Household -> Plot -> Crop

```xlsx
type            name            label
begin_repeat    household       Household
text            hh_id           Household ID
begin_repeat    plot            Plot
text            plot_id         Plot ID
begin_repeat    crop            Crop
text            crop_name       Crop name
decimal         crop_area_ha    Area (ha)
end_repeat      crop
end_repeat      plot
end_repeat      household
```

## Best Practices

1. Keep nesting depth minimal (2 levels when possible).
2. Use clear names for repeat groups and IDs.
3. Add a group label inside repeats for navigation:
   ```xlsx
   type          name          label
   begin_group   plot_group    ${plot_id}
   ...
   end_group
   ```
4. Use `count()` or `sum()` outside repeats for summary checks:
   ```xlsx
   type        name             calculation
   calculate   plot_count       count(${plot_id})
   calculate   total_crop_area  sum(${crop_area_ha})
   ```
5. Avoid heavy calculations inside repeats if performance is a concern.

## Pitfalls

- If a repeat question used for labels is blank, it may not show in lists.
- Relevance in nested repeats can be hard to debug; test each level.
- Keep begin/end pairs balanced; do not move begin/end rows alone.

