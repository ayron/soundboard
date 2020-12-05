#include <stdint.h> // int32_t int8_t
#include <stddef.h> // size_t
#include <stdio.h>

// Converts wave data to array of floats
void scale_frame(
    const char* frame,
    const size_t sample_size,
    const size_t n_channels,
    char* frame_scaled,
    const float volume)
{
  float scale = 2.0 * volume / (1L << (8*sample_size));

  for (int n = 0; n < n_channels; n++)
  {
    int offset = sample_size*n;
    float* sample_scaled = (float*) frame_scaled + n;

    int32_t temp = (int32_t)((int8_t)frame[offset + sample_size-1]);

    for (int i = sample_size-2; i>=0; i--)
    {
      temp <<= 8;
      temp |= 0x000000FF & (int32_t)frame[offset + i];
    }

    *sample_scaled = scale * temp;
  }
}
