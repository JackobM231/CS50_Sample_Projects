#include "helpers.h"
#include <getopt.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>


// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    int average = 0;
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // Compute and set average RGB value for every pixel
            average = ((image[i][j].rgbtBlue + image[i][j].rgbtGreen + image[i][j].rgbtRed) / 3);
            image[i][j].rgbtRed = average;
            image[i][j].rgbtGreen = average;
            image[i][j].rgbtBlue = average;
        }
    }
    return;
}

// Convert image to sepia
void sepia(int height, int width, RGBTRIPLE image[height][width])
{
    int color[3] = {0, 0, 0}; // {red, green, blue}

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // Sepia algorithms
            color[2] = .272 * image[i][j].rgbtRed + .534 * image[i][j].rgbtGreen + .131 * image[i][j].rgbtBlue;
            color[1] = .349 * image[i][j].rgbtRed + .686 * image[i][j].rgbtGreen + .168 * image[i][j].rgbtBlue;
            color[0] =  .393 * image[i][j].rgbtRed + .769 * image[i][j].rgbtGreen + .189 * image[i][j].rgbtBlue;

            // Making sure that any color isn't bigger then 255
            for (int n = 0; n < 3; n++)
            {
                if (color[n] > 255)
                {
                    color[n] = 255;
                }
            }
            image[i][j].rgbtRed = color[0];
            image[i][j].rgbtGreen = color[1];
            image[i][j].rgbtBlue = color[2];
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    // Allocate memory for temp
    RGBTRIPLE(*temp)[width] = calloc(height, width * sizeof(RGBTRIPLE));
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < (width / 2); j++)
        {
            temp[i][j] = image[i][j];
            image[i][j] = image[i][(width - j)];
            image[i][(width - j)] = temp[i][j];
        }
    }

    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    // Allocate memory for temp
    RGBTRIPLE(*temp)[width] = calloc(height, width * sizeof(RGBTRIPLE));
    int x = sizeof(RGBTRIPLE);
    int d = 0;
    int sum_r = 0;
    int sum_g = 0;
    int sum_b = 0;
    int m = -1;
    int n = -1;
     for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            for (m = -1; m < 2; m++)
            {
                for (n = -1; n < 2; n++)
                {
                    if ((sizeof(image[(i + m)][(j + n)])) == (sizeof(image[1][1])))
                    {
                        sum_r += image[(i + m)][(j + n)].rgbtRed;
                        sum_g += image[(i + m)][(j + n)].rgbtGreen;
                        sum_b += image[(i + m)][(j + n)].rgbtBlue;
                        d++;
                    }
                    else
                    {
                        break;
                    }
                }
            }
            temp[i][j].rgbtRed = round(sum_r / d);
            temp[i][j].rgbtGreen = round(sum_g / d);
            temp[i][j].rgbtBlue = round(sum_b / d);
            d = 0;
            sum_r = 0;
            sum_g = 0;
            sum_b = 0;
        }
    }
     for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j].rgbtRed =  temp[i][j].rgbtRed;
            image[i][j].rgbtGreen = temp[i][j].rgbtGreen;
            image[i][j].rgbtBlue = temp[i][j].rgbtBlue;
        }
    }
    return;
}



