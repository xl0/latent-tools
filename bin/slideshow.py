#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import shutil
from typing import List, Optional
import logging

# Custom formatter to avoid duplicating choices in help output
class SingleMetavarHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)

        # If there are choices, only show them once
        if action.choices:
            metavar = '{' + ','.join(action.choices) + '}'
            return ', '.join(action.option_strings) + ' ' + metavar

        default = super()._format_action_invocation(action)
        return default

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('slideshow')

# Define available transition effects with descriptions
TRANSITION_EFFECTS = [
    ("fade", "Standard fade transition between images"),
    ("wipeleft", "Wipe from right to left"),
    ("wiperight", "Wipe from left to right"),
    ("wipeup", "Wipe from bottom to top"),
    ("wipedown", "Wipe from top to bottom"),
    ("slideleft", "Slide the new image from right to left"),
    ("slideright", "Slide the new image from left to right"),
    ("slideup", "Slide the new image from bottom to top"),
    ("slidedown", "Slide the new image from top to bottom"),
    ("circlecrop", "Circular crop effect that reveals the new image"),
    ("rectcrop", "Rectangular crop effect that reveals the new image"),
    ("distance", "Distance-based transition effect"),
    ("fadeblack", "Fade through black between images"),
    ("fadewhite", "Fade through white between images"),
    ("radial", "Radial wipe effect"),
    ("smoothleft", "Smooth wipe from right to left"),
    ("smoothright", "Smooth wipe from left to right"),
    ("smoothup", "Smooth wipe from bottom to top"),
    ("smoothdown", "Smooth wipe from top to bottom"),
    ("circleopen", "Circle opens to reveal the new image"),
    ("circleclose", "Circle closes to reveal the new image"),
    ("vertopen", "Vertical open effect (from center to edges)"),
    ("vertclose", "Vertical close effect (from edges to center)"),
    ("horzopen", "Horizontal open effect (from center to edges)"),
    ("horzclose", "Horizontal close effect (from edges to center)"),
    ("dissolve", "Dissolve effect between images"),
    ("pixelize", "Pixelize the first image into the second"),
    ("diagtl", "Diagonal transition from top-left"),
    ("diagtr", "Diagonal transition from top-right"),
    ("diagbl", "Diagonal transition from bottom-left"),
    ("diagbr", "Diagonal transition from bottom-right"),
    ("hlslice", "Horizontal left slice effect"),
    ("hrslice", "Horizontal right slice effect"),
    ("vuslice", "Vertical up slice effect"),
    ("vdslice", "Vertical down slice effect"),
    ("hblur", "Horizontal blur transition"),
    ("fadegrays", "Fade to grayscale and back"),
    ("wipetl", "Wipe from bottom-right to top-left"),
    ("wipetr", "Wipe from bottom-left to top-right"),
    ("wipebl", "Wipe from top-right to bottom-left"),
    ("wipebr", "Wipe from top-left to bottom-right"),
    ("squeezeh", "Horizontal squeeze effect"),
    ("squeezev", "Vertical squeeze effect"),
    ("zoomin", "Zoom in effect to reveal the new image"),
    ("fadefast", "Fast fade transition"),
    ("fadeslow", "Slow fade transition"),
    ("hlwind", "Horizontal left wind effect"),
    ("hrwind", "Horizontal right wind effect"),
    ("vuwind", "Vertical up wind effect"),
    ("vdwind", "Vertical down wind effect"),
    ("coverleft", "Cover from right to left"),
    ("coverright", "Cover from left to right"),
    ("coverup", "Cover from bottom to top"),
    ("coverdown", "Cover from top to bottom"),
    ("revealleft", "Reveal from left to right"),
    ("revealright", "Reveal from right to left"),
    ("revealup", "Reveal from top to bottom"),
    ("revealdown", "Reveal from bottom to top")
]


def check_ffmpeg() -> bool:
    """Check if ffmpeg is available in the system."""
    return shutil.which('ffmpeg') is not None


def parse_image_list(image_list_file: str) -> List[str]:
    """Parse the image list file and return a list of image paths.

    Args:
        image_list_file: Path to the file containing image paths

    Returns:
        List of image file paths

    Raises:
        FileNotFoundError: If the image list file doesn't exist
        ValueError: If the image list file is empty or has invalid format
    """
    if not os.path.exists(image_list_file):
        raise FileNotFoundError(f"Image list file not found: {image_list_file}")

    with open(image_list_file, 'r') as f:
        lines = f.readlines()

    if not lines:
        raise ValueError(f"Image list file is empty: {image_list_file}")

    # Extract image paths from lines starting with 'file'
    image_files = []
    for i, line in enumerate(lines):
        if line.startswith('file'):
            try:
                # Handle both 'file:path' and "file 'path'" formats
                if "'" in line:
                    image_files.append(line.strip().split("'")[1])
                elif ":" in line:
                    image_files.append(line.strip().split(":", 1)[1].strip())
                else:
                    logger.warning(f"Skipping line {i+1} with unexpected format: {line.strip()}")
            except IndexError:
                logger.warning(f"Skipping line {i+1} with invalid format: {line.strip()}")

    if not image_files:
        raise ValueError(f"No valid image paths found in: {image_list_file}")

    # Verify all images exist
    missing_images = [img for img in image_files if not os.path.exists(img)]
    if missing_images:
        logger.warning(f"Missing image files: {missing_images}")

    return image_files


def create_slideshow(
    image_list_file: str,
    output_file: str,
    frame_duration: float = 3.0,
    transition_duration: float = 0.5,
    transition_type: str = "fade",
    video_quality: int = 18,
    preset: str = "medium",
    overwrite: bool = False,
    verbose: bool = False,
    show_filenames: bool = False,
    filename_mode: str = "full",
    fps: int = 25,
    dry_run: bool = False
) -> bool:
    """Create a slideshow video from a list of images.

    Args:
        image_list_file: Path to the file containing image paths
        output_file: Path to the output video file
        frame_duration: Duration of each frame in seconds
        transition_duration: Duration of transition between frames in seconds
        transition_type: Type of transition effect (fade, wipeleft, etc.)
        video_quality: CRF value for video quality (0-51, lower is better)
        preset: FFmpeg preset (ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow)
        overwrite: Whether to overwrite the output file if it exists
        verbose: Enable verbose logging
        show_filenames: Display filenames in the top left corner of each frame
        filename_mode: How to display filenames: 'full' (complete filename), 'short' (truncated name), or 'number' (frame number)
        dry_run: If True, only print the ffmpeg command without executing it

    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if ffmpeg is available
        if not check_ffmpeg():
            logger.error("ffmpeg not found. Please install ffmpeg and make sure it's in your PATH.")
            return False

        # Check if output directory exists
        output_dir = os.path.dirname(os.path.abspath(output_file))
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")

        # Check if output file exists
        if os.path.exists(output_file) and not overwrite:
            logger.error(f"Output file already exists: {output_file}. Use --overwrite to force.")
            return False

        # Parse image list
        image_files = parse_image_list(image_list_file)
        logger.info(f"Found {len(image_files)} images in the list")
        logger.debug("Images:")
        for img in image_files:
            logger.debug(f"  {img}")

        if len(image_files) < 2:
            logger.error("At least 2 images are required to create a slideshow")
            return False

        # Validate parameters
        if frame_duration < transition_duration:
            logger.error(f"Frame duration ({frame_duration}s) must be greater than or equal to transition duration ({transition_duration}s)")
            return False

        if video_quality < 0 or video_quality > 51:
            logger.warning(f"Video quality CRF value {video_quality} is outside the recommended range (0-51). Lower is better quality.")

        # Build filter complex string
        inputs = []
        filter_parts = []

        # Build inputs for each image
        # Calculate total duration correctly to ensure all frames are shown
        # For a slideshow with transitions, each frame should be shown for its full duration
        # The formula is: sum of all frame durations + any additional time needed for transitions
        total_duration = len(image_files) * frame_duration

        for i, img in enumerate(image_files):
            # Calculate appropriate duration for each input:
            # - First image needs to be available for the entire slideshow duration
            # - Last image only needs to be available for its own frame duration
            # - Middle images need to be available for twice the frame duration (for transitions)
            if i == 0:
                input_duration = total_duration
            elif i == len(image_files) - 1:
                input_duration = frame_duration
            else:
                input_duration = frame_duration * 2

            inputs.append(f"-loop 1 -t {input_duration} -i \"{img}\"")

        # Create filter for each input to prepare it
        for i in range(len(image_files)):
            # Base filter to set PTS and format
            base_filter = f"[{i}:v]setpts=PTS-STARTPTS,format=yuva420p"

            # If showing filenames, add drawtext filter
            if show_filenames:
                # Determine what text to display based on filename_mode
                if filename_mode == "full":
                    # Extract just the filename without path
                    display_text = os.path.basename(image_files[i])
                elif filename_mode == "short":
                    # Extract filename without extension and truncate if needed
                    base_name = os.path.splitext(os.path.basename(image_files[i]))[0]
                    display_text = base_name[:20] + "..." if len(base_name) > 20 else base_name
                elif filename_mode == "number":
                    # Just show the frame number
                    display_text = f"Frame {i+1}/{len(image_files)}"
                else:
                    # Default to basename if mode is not recognized
                    display_text = os.path.basename(image_files[i])

                # Add drawtext filter with text in top left corner
                base_filter += f",drawtext=text='{display_text}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=10:y=10"

            # Complete the filter
            filter_parts.append(f"{base_filter}[v{i}];")

        # Calculate frame-based durations for precise timing
        frame_duration_frames = int(frame_duration * fps)
        transition_duration_frames = int(transition_duration * fps)

        # Create xfade filters to transition between images
        last_output = f"[v0]"
        for i in range(1, len(image_files)):
            # Calculate precise offset in frames and convert back to seconds for exact timing
            # Each frame should start at its exact position: i * frame_duration
            offset_frames = i * frame_duration_frames
            offset = offset_frames / fps
            filter_parts.append(
                f"{last_output}[v{i}]xfade=transition={transition_type}:duration={transition_duration}:offset={offset}[v{i}out];"
            )
            last_output = f"[v{i}out]"

        # Calculate the expected duration for verification
        # The total duration is simply the number of frames times the frame duration
        expected_duration = len(image_files) * frame_duration
        expected_frames = int(expected_duration * fps)
        logger.debug(f"Number of images: {len(image_files)}, Frame duration: {frame_duration}s, Transition duration: {transition_duration}s")
        logger.debug(f"Expected slideshow duration: {expected_duration:.2f} seconds ({expected_frames} frames at {fps} fps)")

        filter_complex = "".join(filter_parts)

        # Build ffmpeg command
        overwrite_flag = "-y" if overwrite else "-n"

        # Add precise timing control to ensure exact duration
        cmd = f"ffmpeg {overwrite_flag} {' '.join(inputs)} -filter_complex \"{filter_complex[:-1]}\" -map \"{last_output}\" \
              -r {fps} -pix_fmt yuv420p -c:v libx264 -crf {video_quality} -preset {preset} \
              -frames:v {expected_frames} -t {expected_duration} \"{output_file}\""

        logger.info(f"Creating slideshow with {len(image_files)} images")
        logger.debug(f"Running command: {cmd}")

        # If dry run, just print the command and return
        if dry_run:
            print("\n--dry-run: No action taken.")
            return True

        # Execute ffmpeg command
        process = subprocess.run(cmd, shell=True, text=True)

        if process.returncode != 0:
            logger.error(f"ffmpeg failed with error: {process.stderr}")
            return False

        # Try to get the actual duration of the created video
        try:
            duration_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{output_file}"'
            actual_duration = float(subprocess.check_output(duration_cmd, shell=True, text=True).strip())
            logger.info(f"Slideshow created successfully: {output_file} (duration: {actual_duration:.2f}s)")
        except Exception as e:
            # If we can't get the duration, just log success without it
            logger.info(f"Slideshow created successfully: {output_file}")

        return True

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return False
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return False


def list_effects():
    """Print all available transition effects with descriptions"""
    print("\nAvailable Transition Effects:\n")
    print("{:<15} {}".format("EFFECT", "DESCRIPTION"))
    print("{:<15} {}".format("-"*15, "-"*50))
    for effect, desc in TRANSITION_EFFECTS:
        print("{:<15} {}".format(effect, desc))
    print()
    sys.exit(0)

def main():
    """Main function to handle command-line arguments."""
    # Create parser first to handle --list-effects anywhere in the command
    parser = argparse.ArgumentParser(
        description="Create a slideshow video from a list of images",
        formatter_class=SingleMetavarHelpFormatter,
        epilog="Use the --list-effects option to see detailed descriptions of all transition effects"
    )

    # Add --list-effects as an option
    parser.add_argument(
        "--list-effects",
        action="store_true",
        help="List all available transition effects with descriptions and exit"
    )

    parser.add_argument(
        "image_list",
        help="Path to a file containing a list of images (one per line, format: file 'path/to/image.jpg')"
    )
    parser.add_argument(
        "output",
        help="Path to the output video file"
    )
    parser.add_argument(
        "-d", "--duration",
        type=float,
        default=3.0,
        help="Duration of each frame in seconds"
    )
    parser.add_argument(
        "-t", "--transition",
        type=float,
        default=0.5,
        help="Duration of transition between frames in seconds"
    )

    parser.add_argument(
        "-e", "--effect",
        default="fade",
        choices=[effect for effect, _ in TRANSITION_EFFECTS],
        help="Transition effect to use between images. Use the --list-effects option to see all available effects with descriptions."
    )
    parser.add_argument(
        "-q", "--quality",
        type=int,
        default=18,
        help="CRF value for video quality (0-51, lower is better)"
    )
    parser.add_argument(
        "-p", "--preset",
        default="medium",
        choices=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"],
        help="FFmpeg preset (faster presets = lower quality, faster encoding)"
    )
    parser.add_argument(
        "-o", "--overwrite",
        action="store_true",
        help="Overwrite output file if it exists"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--show-filenames", "-f",
        action="store_true",
        help="Display filenames in the top left corner of each frame"
    )

    parser.add_argument(
        "--filename-mode",
        choices=["full", "short", "number"],
        default="full",
        help="How to display filenames: 'full' (complete filename), 'short' (truncated name), or 'number' (frame number)"
    )

    parser.add_argument(
        "--fps",
        type=int,
        default=25,
        help="Output video frame rate"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the ffmpeg command without executing it"
    )

    args = parser.parse_args()

    # Check if the user wants to list effects
    if args.list_effects:
        list_effects()

    # Set logging level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Create slideshow
    success = create_slideshow(
        image_list_file=args.image_list,
        output_file=args.output,
        frame_duration=args.duration,
        transition_duration=args.transition,
        transition_type=args.effect,
        video_quality=args.quality,
        preset=args.preset,
        overwrite=args.overwrite,
        verbose=args.verbose,
        show_filenames=args.show_filenames,
        filename_mode=args.filename_mode,
        fps=args.fps,
        dry_run=args.dry_run
    )

    # Return appropriate exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()