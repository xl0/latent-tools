#!/usr/bin/env python3
import argparse, logging, multiprocessing, os, shutil, subprocess, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
from typing import List, Tuple, Optional
class SingleMetavarHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0: return super()._format_action_invocation(action)
        if action.choices: return f"{', '.join(action.option_strings)} {{{','.join(action.choices)}}}"
        return super()._format_action_invocation(action)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
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


def create_temp_directory(base_dir=".") -> str:
    temp_dir = os.path.join(base_dir, "_temp")
    if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    return temp_dir

def create_transition_clip(index, img1: str, img2: str, output_file: str,
                      frame_duration: float, transition_duration: float,
                      transition_type: str, fps: int, video_quality: int,
                      preset: str, show_filenames: bool, filename_mode: str,
                      dry_run: bool = False) -> Tuple[int, bool]:
    """Create a transition clip between two images."""
    try:
        inputs = [
            f"-loop 1 -t {frame_duration + transition_duration} -i \"{img1}\"",  # First image
            f"-loop 1 -t {transition_duration} -i \"{img2}\""                  # Second image
        ]

        filter_parts = []

        for i in (0, 1):
            base_filter = f"[{i}:v]setpts=PTS-STARTPTS,format=yuva420p"

            if show_filenames:
                base_name = os.path.basename(img1 if i == 0 else img2)
                if filename_mode == "short":
                    display_text = base_name[:20] + "..." if len(base_name) > 20 else base_name
                elif filename_mode == "number":
                    display_text = f"Image {i+1}/2"
                else:
                    display_text = base_name

                base_filter += f",drawtext=text='{display_text}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=10:y=10"

            filter_parts.append(f"{base_filter}[v{i}];")

        filter_parts.append(
            f"[v0][v1]xfade=transition={transition_type}:duration={transition_duration}:offset={frame_duration}[vout];"
        )

        expected_duration = frame_duration + transition_duration
        expected_frames = int(expected_duration * fps)
        filter_complex = "".join(filter_parts)

        cmd = f"ffmpeg -y {' '.join(inputs)} -filter_complex \"{filter_complex[:-1]}\" -map \"[vout]\" \
              -r {fps} -pix_fmt yuv420p -c:v libx264 -crf {video_quality} -preset {preset} \
              -frames:v {expected_frames} -t {expected_duration} \"{output_file}\""

        logger.debug(f"Creating transition: {os.path.basename(img1)} -> {os.path.basename(img2)}")
        
        if dry_run:
            print(f"\n--dry-run: {cmd}")
            return (index, True)

        process = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        return (index, process.returncode == 0)

    except Exception as e:
        logger.error(f"Error creating transition clip: {e}")
        return (index, False)

def concatenate_clips(clip_files: List[str], output_file: str, video_quality: int, preset: str, dry_run: bool = False) -> bool:
    """Concatenate multiple video clips into a single video."""
    try:
        temp_dir = os.path.dirname(clip_files[0])
        concat_file_path = os.path.join(temp_dir, 'concat_list.txt')

        with open(concat_file_path, 'w') as concat_file:
            for clip in clip_files:
                concat_file.write(f"file '{os.path.abspath(clip)}'\n")

        logger.info(f"Concatenating {len(clip_files)} clips into final video")
        cmd = f'ffmpeg -y -f concat -safe 0 -i {concat_file_path} -c:v libx264 -crf {video_quality} -preset {preset} "{output_file}"'

        if dry_run:
            logger.info(f"\n--dry-run: {cmd}")
            return True

        process = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        
        if process.returncode != 0:
            logger.error(f"ffmpeg failed with error: {process.stderr}")
            return False

        logger.info(f"Slideshow created successfully: {output_file}")
        return True

    except Exception as e:
        logger.error(f"Error concatenating clips: {e}")
        return False

def parse_image_list(image_list_file: str) -> List[str]:
    with open(image_list_file, 'r') as f:
        image_files = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    if not image_files:
        raise ValueError(f"Image list file is empty: {image_list_file}")

    missing_images = [img for img in image_files if not os.path.exists(img)]
    if missing_images:
        raise FileNotFoundError(f"Missing image files: {missing_images}")

    return image_files


def index_to_filename(i: int, temp_dir: str) -> str: return f"{temp_dir}/transition_{i:04d}.mp4"

def create_slideshow(
    image_list_file: str,
    output_file: str,
    frame_duration: float = 3.0,
    transition_duration: float = 0.5,
    transition_type: str = "fade",
    video_quality: int = 18,
    preset: str = "medium",
    overwrite: bool = False,
    show_filenames: bool = False,
    filename_mode: str = "full",
    fps: int = 25,
    dry_run: bool = False
) -> bool:
    """Create a slideshow video from a list of images using parallel processing."""
    try:
        if shutil.which('ffmpeg') is None:
            logger.error("ffmpeg not found. Please install ffmpeg and make sure it's in your PATH.")
            return False

        output_dir = os.path.dirname(os.path.abspath(output_file))
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")

        if os.path.exists(output_file) and not overwrite:
            logger.error(f"Output file already exists: {output_file}. Use --overwrite to force.")
            return False

        image_files = parse_image_list(image_list_file)
        logger.info(f"Found {len(image_files)} images in the list")
        
        if len(image_files) < 2:
            logger.error("At least 2 images are required to create a slideshow")
            return False

        if frame_duration < transition_duration:
            logger.error(f"Frame duration ({frame_duration}s) must be greater than transition duration ({transition_duration}s)")
            return False

        if video_quality < 0 or video_quality > 51:
            logger.warning(f"Video quality CRF value {video_quality} is outside the recommended range (0-51). Lower is better quality.")

        temp_dir = create_temp_directory()
        logger.info(f"Processing {len(image_files)-1} transitions in parallel")

        transition_args = []
        for i in range(len(image_files) - 1):
            transition_args.append((
                i,
                image_files[i], 
                image_files[i+1], 
                index_to_filename(i, temp_dir),
                frame_duration,
                transition_duration,
                transition_type,
                fps,
                video_quality,
                preset,
                show_filenames,
                filename_mode,
                dry_run
            ))

        max_workers = min(multiprocessing.cpu_count(), len(transition_args))
        logger.info(f"Using {max_workers} parallel processes")

        clip_files = []
        failed_transitions = 0

        if dry_run:
            logger.info("Dry run mode: Processing only one transition as example")
            index, success = create_transition_clip(*transition_args[0])
            if success:
                clip_files.append(index)
            else:
                failed_transitions += 1
        else:
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(create_transition_clip, *args) for args in transition_args]

                with tqdm(total=len(futures), desc="Creating transitions", unit="clip") as progress:
                    for future in as_completed(futures):
                        try:
                            index, success = future.result()
                            if success:
                                clip_files.append(index)
                            else:
                                failed_transitions += 1
                                logger.error(f"Failed to process transition {index+1}/{len(transition_args)}")
                        except Exception as e:
                            failed_transitions += 1
                            logger.error(f"Exception in transition processing: {e}")
                        progress.update(1)

        if failed_transitions > 0:
            logger.error(f"Failed to process {failed_transitions} transitions")
            return False

        clip_files.sort()
        clip_files = [index_to_filename(i, temp_dir) for i in clip_files]

        if dry_run:
            logger.info("Dry run mode: Skipping concatenation step")
            print("\n--dry-run: Would concatenate the following clips:")
            for clip in clip_files:
                print(f"  {clip}")
            return True

        success = concatenate_clips(
            clip_files=clip_files,
            output_file=output_file,
            video_quality=video_quality,
            preset=preset,
            dry_run=dry_run
        )

        if not success:
            logger.error("Failed to concatenate transition clips")
            return False

        # Note: We don't delete the temp directory at the end to make debugging easier
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
    print("\nAvailable Transition Effects:\n")
    print("{:<15} {}".format("EFFECT", "DESCRIPTION"))
    print("{:<15} {}".format("-"*15, "-"*50))
    for effect, desc in TRANSITION_EFFECTS:
        print("{:<15} {}".format(effect, desc))
    print()
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description="Create a slideshow video from a list of images",
        formatter_class=SingleMetavarHelpFormatter,
        epilog="Use the --list-effects option to see detailed descriptions of all transition effects"
    )

    parser.add_argument("--list-effects", action="store_true",
                      help="List all available transition effects with descriptions and exit")
    parser.add_argument("image_list",
                      help="Path to a file containing a list of images (one per line)")
    parser.add_argument("output", 
                      help="Path to the output video file")
    parser.add_argument("-d", "--duration", type=float, default=3.0,
                      help="Duration of each frame in seconds")
    parser.add_argument("-t", "--transition", type=float, default=0.5,
                      help="Duration of transition between frames in seconds")
    parser.add_argument("-e", "--effect", default="fade",
                      choices=[effect for effect, _ in TRANSITION_EFFECTS],
                      help="Transition effect to use between images")
    parser.add_argument("-q", "--quality", type=int, default=18,
                      help="CRF value for video quality (0-51, lower is better)")
    parser.add_argument("-p", "--preset", default="medium",
                      choices=["ultrafast", "superfast", "veryfast", "faster", "fast", 
                               "medium", "slow", "slower", "veryslow"],
                      help="FFmpeg preset (faster presets = lower quality, faster encoding)")
    parser.add_argument("-o", "--overwrite", action="store_true",
                      help="Overwrite output file if it exists")
    parser.add_argument("-v", "--verbose", action="store_true",
                      help="Enable verbose logging")
    parser.add_argument("--show-filenames", "-f", action="store_true",
                      help="Display filenames in the top left corner of each frame")
    parser.add_argument("--filename-mode", choices=["full", "short", "number"], default="full",
                      help="How to display filenames: 'full', 'short', or 'number'")
    parser.add_argument("--fps", type=int, default=25,
                      help="Output video frame rate")
    parser.add_argument("--dry-run", action="store_true",
                      help="Print the ffmpeg command without executing it")

    args = parser.parse_args()

    if args.list_effects:
        list_effects()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    success = create_slideshow(
        image_list_file=args.image_list,
        output_file=args.output,
        frame_duration=args.duration,
        transition_duration=args.transition,
        transition_type=args.effect,
        video_quality=args.quality,
        preset=args.preset,
        overwrite=args.overwrite,
        show_filenames=args.show_filenames,
        filename_mode=args.filename_mode,
        fps=args.fps,
        dry_run=args.dry_run
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()