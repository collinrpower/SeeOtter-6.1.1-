# SeeOtter Model Training User Guide: Iterative Active Learning for Wildlife Detection

## 1. Setup and Initialization
- Install SeeOtter on a Windows PC that meets system requirements.
- Copy the SeeOtter folder to your computer.
- Launch `SeeOtter.exe`.

## 2. Create a New Survey from an Unannotated Dataset
1. From the Survey Manager, click the blue **+** button.
2. In **New Survey**:
   - Enter **Survey Name**.
   - Set **Project Path** (must be an existing folder).
   - Set **Images Path** (defaults to `[ProjectPath/Images]`).
3. Click **Create New Survey**.

## 3. Generate Initial Annotations
1. Open the new survey (folder icon → `savefile.json`).
2. Run **Processing** (green play button) to generate predictions:
   - Pre-Processing → Processing (image detection) → Post-Processing.
3. Switch to **OtterChecker9000** to review predictions:
   - Mark each as **Correct**, **Incorrect**, or **Ambiguous**.
   - Save/export validated annotations (saved in **Annotations** folder).

## 4. Train the Initial Model
1. Export the validated annotations to form your training dataset.
2. Split the dataset into **training** and **validation** sets.
3. Run the training script (e.g., `Train_SeeOtter_Model.py`) with these annotations.
4. Save the trained model weights (e.g., `initial_best.pt`).
5. Evaluate model performance on the validation set.

## 5. Active Learning Iterative Cycle
1. **Run Detection with Current Model**
   - Replace old model weights in SeeOtter with the updated `.pt` file.
   - Process new/unannotated images in SeeOtter.
2. **Annotation Review**
   - Use **OtterChecker9000** to mark new predictions as Correct/Incorrect/Ambiguous.
3. **Update Training Dataset**
   - Merge the newly validated annotations with your existing training dataset.
4. **Retrain**
   - Re-run the training script with the updated dataset.
   - Save the new model weights.
5. **Evaluate**
   - Validate on the validation set, tracking performance.
6. **Repeat** until performance meets requirements.

## 6. Final Evaluation and Deployment
1. Test the final model on a separate test dataset.
2. Save final model weights (e.g., `final_best.pt`).
3. Update **OtterChecker9000** to reference the final model.
4. Deploy the final model in SeeOtter for live wildlife detection.
